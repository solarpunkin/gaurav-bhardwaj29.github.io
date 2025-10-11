---
title: "bencoding"
tags: [networks, C]
slug: "bencoding"
weblog_title: "Bencoding"
---

<figure style="text-align: center;">
  <img src="https://pub-91e1a485198740aabff1705e89606dc3.r2.dev/beencoder/beencode.webp" style="max-width: 100%; height: auto;" />
  <figcaption>BEncode Editor was a windows tool to view and edit .torrent files</figcaption>
</figure>

Bencoding (pronounced be-encoding) is a rather simple type of encoding used by P2P file sharing system BitTorrent to encode `.torrent` file metadata in a non-human readable form, at the same time allowing complex yet loosely structured data to be stored in a platform independent way. 

Bencode uses ASCII and supports four types of data structures:

- Integers
- String
- List
- Dictionaries

`.torrent` files are bencoded dictionaries. Since each possible value has only a single valid bencoding (one-to-one mapping), applications can directly match the encoded forms without ever decoding their values. For BitTorrent, there are mainly two types of parsers used today — [streaming](https://github.com/willemt/streaming-bencode) which parses data as it arrives in the network, and [non-streaming](https://github.com/willemt/heapless-bencode) which stores the entire metadata in memory and parses afterwards. 

## how bencoding works

<figure style="text-align: center;">
  <img src="https://pub-91e1a485198740aabff1705e89606dc3.r2.dev/beencoder/example%20.torrent%20file.png" style="max-width: 100%; height: auto;" />
  <figcaption></figcaption>
</figure>

The algorithm as defined in [BitTorrent v1.0](https://wiki.theory.org/BitTorrentSpecification) uses ASCII characters as delimiters and digits to encode data structures. 

- <span class="underline">Strings</span> are length-prefixed base ten followed by a colon and the string. For example, 4:spam corresponds to 'spam'.

- <span class="underline">Integers</span> are represented by an 'i' followed by the number in base 10 followed by an 'e'. For example, i3e corresponds to 3 and i-3e corresponds to -3. Integers have no size limitation. i-0e is invalid. All encodings with a leading zero, such as i03e, are invalid, other than i0e, which of course corresponds to 0.

- <span class="underline">Lists</span> are encoded as an 'l' followed by their elements (also bencoded) followed by an 'e'. For example, l4:spam4:eggse corresponds to ['spam', 'eggs'].

- <span class="underline">Dictionaries</span> are encoded as a 'd' followed by a list of alternating keys and their corresponding values followed by an 'e'. For example, d3:cow3:moo4:spam4:eggse corresponds to {'cow': 'moo', 'spam': 'eggs'} and d4:spaml1:a1:bee corresponds to {'spam': ['a', 'b']}. Keys must be strings and appear in sorted order (sorted as raw strings, not alphanumerics).

**Non-streaming (DOM-style):** The parser reads the entire `.torrent` metadata file into memory and constructs a full hierarchical representation (like a JSON DOM). Each dictionary, list, and string are allocated fixed-sized bufferes and becomes a separate in-memory object allocated on the heap. You then traverse this tree to extract metadata info. This approach is simple and ideal for small files or tracker lists, where the full dataset easily fits in memory.

**Streaming (SAX-style):** Parses the bencoded data “on the fly” as bytes arrive from the network socket or file. You feed it buffers of bytes, it maintains a small internal parsing stack or state machine and fires callbacks (e.g., on dictionary start/end, key, or value). It doesn’t build an in-memory tree of the bencoded object so it’s more memory efficient and suitable for large continuous streams, but it doesn’t allow random access or post-hoc traversal of the data structure. Distributed Hast Tables have very large messages and loading everything in memory at once is resource-intensive and might introduce network congestion which large number of updates so using a SAX-style parser is better in this case.

