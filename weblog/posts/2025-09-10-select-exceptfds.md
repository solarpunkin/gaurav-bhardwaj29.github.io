---
title: "select exceptfds"
tags: [C, UNIX, ipc]
slug: "select-exceptfds"
weblog_title: "I tried to actually make select()’s exceptfds trigger"
---

**And here's what happened**

I saw this line in the man page:

<figure style="text-align: center;">
  <img src="https://pub-91e1a485198740aabff1705e89606dc3.r2.dev/select-exceptfds-man.png" style="max-width: 100%; height: auto;" />
  <figcaption></figcaption>
</figure>

But I never saw it actually trigger. So I decided to write a tiny TCP client/server, and try to make `select()` wake up on the `exceptfds` set.

TCP’s “out-of-band” data isn’t a second stream or a priority lane. It’s just one single byte flagged as urgent. The sender sets the urgent pointer in the TCP header.

On the receiving end, two options exist:

- Default: urgent byte is only visible if you call `recv(MSG_OOB)`.
- With `SO_OOBINLINE`: urgent byte is delivered inline with the regular stream, but `select()` still signals it as “exceptional.”

That’s it. One byte, not a side channel.

### pseudocode:
##### server:

```c
socket()
bind()
listen()

fd_set rfds, efds;
while (true) {
    FD_ZERO(&rfds); FD_ZERO(&efds);
    FD_SET(c, &rfds); FD_SET(c, &efds);

    select(c+1, &rfds, NULL, &efds, NULL);

    if (FD_ISSET(c, &efds)) {
        char b;
        int n = recv(c, &b, 1, MSG_OOB);
        printf("OOB: got '%c'\n", b);
    }
    if (FD_ISSET(c, &rfds)) {
        char buf[64];
        int n = recv(c, buf, sizeof buf, 0);
        if (n <= 0) break;
        printf("INBAND: %.*s\n", n, buf);
    }
}
```

##### client:

```c
int s = socket(AF_INET, SOCK_STREAM, 0);
connect(s, ...);

send(s, "hello", 5, 0);
send(s, "!", 1, MSG_OOB);   // the urgent byte
send(s, "world", 5, 0);
```

Run the server, connect the client, and watch the logs:

```bash
INBAND: hello
OOB: got '!'
INBAND: world
```

Here's the thing: 

- the exceptfds set was marked only when the OOB byte arrived,
- a call to `recv(MSG_OOB)` returned it cleanly, and
- if I had enabled `SO_OOBINLINE`, then `recv(MSG_OOB)` stopped working and the ! showed up inside the normal stream—but exceptfds still got flagged.

So the man page was right: exceptfds is just “would recv(MSG_OOB) not block.”

I ran tcpdump -vv while sending. The OOB send set the TCP URG flag and advanced the urgent pointer. You can see it in the packet dump:

```bash
Flags [P.], urg 1, seq 6:7, urgptr=1
```

### BSD vs Linux

There’s an old historical quirk: BSD stacks interpret the urgent pointer differently. On FreeBSD/macOS, the “urgent byte” is actually delivered as the last byte of the stream, not a separate one.

### why it matters (or doesn’t)

In the old days, telnet used OOB for control signals. Today, hardly anything does. It’s deprecated in RFC 6093.

But as an experiment:

- i confirmed `select()`’s exceptfds really does fire.
- it only wakes up when there’s urgent data waiting to be `recv(MSG_OOB)`’d.
- it clears once consumed.
- and it’s just one byte — no queue, no stream.

and if you ever see it in production? Chances are you’re debugging legacy telnet, or something’s gone wrong.