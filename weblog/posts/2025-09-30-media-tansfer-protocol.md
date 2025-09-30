---
title: "MTP over USB"
tags: [UNIX]
slug: "media-transfer-protocol"
weblog_title: "the case for slow start in USB file transfer"
---

**Media Transfer Protocol**, or MTP, is the default way of sharing media files, such as photos and other files, via USB from an Android phone to a host machine, which can be your laptop or desktop.
You might wonder if this is the same as copying files from one place to another on the same machine or moving files between drives. It is actually a very different approach for how we send files through link layers from one device to another when they are physically connected by a USB cable.

When you connect your Android phone via USB to a host machine and start sending files, you'll notice on your Mac that the progress bar sweeps for some time, saying it's "loading" or "copying" a file. It says this for quite some time, and you don't see the progress bar move from 0% to 100%. We call this the "staging" or "preparation" stage because the progress bar sweeps indefinitely, and it can feel like the system has hung up before the real transfer has even started.

What actually happens in this phase is a communication process between two parties: the initiator and the responder. MTP communicates using commands and responses between these two parties. Typically, the PC is the initiator, and your phone is the responder, though it can be the other way around. A device can never assume both roles at the same time.
The initiator starts the communication by sending a command, and the responder replies, acknowledging the connection. It's important to know that MTP transfers are unidirectional, and the direction of data flow must be known and accepted by both the initiator and the responder beforehand.

For example, let's say the initiator (your PC) asks for a file from the responder (your phone). The phone will first share the file's metadata, acknowledging the request by responding with the file's name, size, format code, and modification time. These handshakes happen before the actual file transfer takes place. The handshakes are serialized, not pipelined, and these round trips of sharing metadata and initial header files require multiple back-and-forth communications between the host and the phone's MTP responder. The PC might even request small snippets of data blocks to verify headers and expected sizes. All of this happens synchronously.

After the PC has received the metadata and knows the size of the file, it stages the physical memory, allocating the specific amount of space on the device to initiate the file transfer. You see the sweeping UI progress bar during this entire allocation process. This step is not visible in userland but is expensive. It may involve page faults, wired memory pinning, DMA descriptor setup, and many other kernel and driver-level buffer allocations and file system operations. This ensures the receiving device has allocated the necessary memory and is ready for the transfer.

Once staging is complete, the second phase starts, which is responsible for actually transferring the file from the sender to the receiver. This stage happens very fast, almost instantly, with transfer speeds around **1 to 2 GB per second** on modern devices, and it incurs low overhead cost.

Because the staging delays are front-loaded, the copy process appears instantaneous once it begins. The progress bar is tied directly to the number of bytes delivered and seems to jump from 0% to 100% almost instantly. It appears fast relative to the staging phase because it fully utilizes the USB endpoint's bandwidth, and all the small, serialized, latency-heavy exchanges have already been completed.
