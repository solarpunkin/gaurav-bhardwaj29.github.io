---
title: "how to find the fastest way to make systems talk"
tags: [github, ipc, C]
slug: "make-systems-talk-fast"
---

So, I was learning about interprocess communications in Unix-like systems by reading and implementing concepts from Beej’s guide to interprocess communication. He explains explains primitives like pipes, FIFOs, sockets, and shared memory with approachable code examples, making it easy for me to understand how our systems work. What struck me was how these different processes that are similar in function were drastically (or mildly) comparable to each other in empirical terms. What I mean by this is for example, stream sockets beat TCP loopback in both latency and throughput, or pipes are very efficient for tiny payloads but throughput declines once messages exceed the default 64KB pipe buffer [man7/pipe](https://man7.org/linux/man-pages/man7/pipe.7.html), or FIFO (named pipes) sometimes show lower latency than anonymous pipes by ~1.5× in practice.

It’s true that many of these metrics are OS-specific and don’t generalise across different OS or even versions of the same OS. This is because system-level factors like kernel scheduling, IPC subsystem implementations, CPU frequency scaling, and timer precision vary by OS and version, influencing results despite using identical benchmarking code and configurations. This isn’t a concern if you’re just trying out a software you downloaded from the web or writing application code that abstracts away much of the low-level work these IPC handles, or for a million other reasons. However, if you’re an indie gamer or write low-level code that relies heavily on process dependence, like choosing communication primitives for an app design, then something like the choice of Shared Memory over domain sockets can make or break your app performance. As I mentioned, these scores are heavily platform-biased, and the information available online isn’t a measure for your specific kernel or use case. Benchmarking your computer’s IPC reveals your system bottlenecks and helps you identify the fastest communication mechanism for your workflow.

<figure style="text-align: center;">
  <img src="https://pub-91e1a485198740aabff1705e89606dc3.r2.dev/pipes-fifo/pipesfifo.jpg" style="max-width: 100%; height: auto;" />
  <figcaption></figcaption>
</figure>

I did some research and found an IPC efficiency test on [GitHub](https://github.com/goldsborough/ipc-bench). However, the repository was quite old and optimised to target a specific OS. Not to mention that the CPU and kernel become more efficient with each iteration (in the case of MacBooks, this happens every year). That being said, this was the closest IPC test I could find. So, I decided to create my own IPC Stress Tester. I wanted it to be as unbiased as possible, adding recently introduced processes, so that it generalises to a wider range of OS and their versions. This forced me to use consistent methods and often the same measurement code to minimise differences. Now, people can profile their IPC and not rely solely on what works best in theory because, to be honest, theory doesn’t catch up to industry standards and is just as good as empirical results. Now, you can compare different computers to see which has a faster CPU+OS.

#### What are we measuring?

- Message Latency (p99, in µs): critical for request/response workloads like RPC or gaming

- Throughput (msg/s or MB/s): matters when moving bulk data, e.g., media or databases.

- Payload scaling (1 byte –> 1MB): small vs large messages stress IPC differently (control messages vs bulk transfer).

- Process count scaling (1:1, 1:N, N:N): shows effects of kernel scheduling, contention, and fairness.

