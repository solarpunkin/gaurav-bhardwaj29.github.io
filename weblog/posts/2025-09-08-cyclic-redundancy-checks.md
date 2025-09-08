---
title: "cyclic redundancy checks"
tags: [C, networks]
slug: "crc32"
weblog_title: "Table-Driven CRC32 for a minimal TCP File Sender"
---

Wish I had the intuition to just summon god-tier generator polynomials for cyclic redundancy checks. But nah, shoutout to [Philip Koopman](https://users.ece.cmu.edu/~koopman/crc/) for actually coming up with best polynomials. They are excellent for detecting single-bit, two-bit and burst errors. Especially the CRC32 polynomial is used in virtually every stack to detect bit manipulation errors where file transfers take place. 

<figure style="text-align: center;">
  <img src="https://pub-91e1a485198740aabff1705e89606dc3.r2.dev/crc32/rotated_horizontal.png" style="max-width: 100%; height: auto;" />
  <figcaption>had to do it, sorry:p</figcaption>
</figure>

I was experimenting with different polynomials to hack the pattern (if there is) to find the relationship between error and the actual bytes that got flipped. I ported the GNU libiberty xcrc32 [(here ‘x’ is wrapper around the standard function)](https://gcc.gnu.org/onlinedocs/libiberty/Memory-Allocation.html) [source code](https://raw.githubusercontent.com/gcc-mirror/gcc/refs/heads/master/libiberty/crc32.c) with some modifications into my client-server program to send a PNG file internally. 

What I modified:

- CRC seed = The `xcrc32()` implementation from GNU libiberty isn’t the “standard Ethernet CRC-32” with reflection and XOR. I changed the initial value = **0xFFFFFFFF**.
- I set the file size to **8-byte** `uint64_t`, and added proper `htonll_u64()` conversion for network order.

<figure style="text-align: center;">
  <img src="https://pub-91e1a485198740aabff1705e89606dc3.r2.dev/crc32/endian.png" style="max-width: 100%; height: auto;" />
  <figcaption>host to network byte order</figcaption>
</figure>

You can safely use this modified CRC32 to check correctness for:

- Any binary file (images, executables, archives)
- Any text file
- Arbitrary in-memory messages (structs, packets, frames)

Basically, *“if you can serialize it to bytes, you can protect it with this CRC.”*

This youtube video demonstrates how the algorithm works in [theory](https://www.youtube.com/watch?v=izG7qT0EpBw) and in [hardware](https://www.youtube.com/watch?v=sNkERQlK8j8). Highly recommend!