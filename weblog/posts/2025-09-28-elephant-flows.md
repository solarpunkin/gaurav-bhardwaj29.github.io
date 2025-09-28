---
title: "handling network congestion"
tags: [internet, networks]
slug: "elephant-flows"
weblog_title: "problem of finding the top-k heavy hitters"
---

Imagine you are running a company that provides access to the internet. There is going to be a network of connected devices with millions of users sending billions of packets per second. Person A wants to download a movie and Person B is sending an email. Likewise there will be flows requiring higher bandwidth (movie download) than others. A flow is a collection of packets of the same kind. Skype sends flows of video packets that is different from spotify sending flows of audio packets.

Your job as an internet service provider is to ensure the network is running smoothly while serving millions of users. You would want to know which users or flows are eating the most bandwidth for capacity planning so that light users are not jeopardized by network congestion. 

Now at the network layer all the packets are just frames of 1s and 0s. They are also unreliably transmitted from the source device to the destination device. The flows are not streamlined, i.e. a video packet may be followed by a message packet. Keeping exact counters for each flow would require massive memory – impossible at line speed. We are always bounded by the memory and speed of the network. But we would want to keep a track of the most heavy flows. We need a very efficient data structure and a fast update algorithm to keep pace with the sheer amount of network surge.

We are going to make a tradeoff here. We are not counting each flow, instead we keep an approximate record of the top K most recurring flows in a network. This approximation is proved to be in our favour of getting high accuracy, working at line speed and using only a small fixed amount of memory.

The problem of finding heavy hitters can be mapped to many other areas beyond networking and distributed systems. For example, we can answer questions like:

1. What are the K hashtags people have mentioned the most in the last X hours?
2. What are the K most trending spotify songs in the last X hours?
3. What are the K news with highest read/view count today?