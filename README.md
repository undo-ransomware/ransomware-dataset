# Ransomware samples dataset

Our ransomware dataset is based on [VirusShare](https://virusshare.com)'s collection of 33.9M samples.
We used John Seymour's [dataset](https://twitter.com/_delta_zero/status/1113477389961416704) containing the VirusTotal [labels](https://www.zerofox.com/blog/labeling-virusshare-corpus/) of all 33.2M samples from June 2012 to February 2019.

We downloaded the [Raw dataset](https://drive.google.com/drive/folders/1oKr5hP8Dlz1QABUOX-HKi2n8tyRkbaDN) and filtered it for all `ransom` detections.
These 456856 samples are then further filtered for Windows executables using the [VirusShare filetypes dataset](https://a4lg.com/downloads/vxshare/).
Filtering by filetype is mostly meant to remove a significant number of browser-based HTML ransom demands, which are scary but harmless (in an up-to-date browser).

The resulting 339594 samples were then classified using the [AVClass malware labeling tool](https://github.com/malicialab/avclass) to group them by family.
This yielded 23616 `SINGLETON`s (samples with generic names only), 1562 "families" containing only one sample, and 1671 ransomware families with 2 or more members.
Filtering out the `SINGLETON`s leaves a base set of 315978 samples.

![almost but not quite a power law](ransomware-family-distribution.png)

To the surprise of absolutely no one, it's the usual long-tailed distribution.
What is surprising is that the 2-sample families do contain some ransomware that did make the news, eg. *GoldenEye*, *ZeroLocker* and *Bad Rabbit*.
The 1-sample families contain many generic names like `940677ecdf` or `aawj`, but also known ransomware like *Alcatraz Locker*.

The head end:

![Zeus, Winwebsec, Virlock, ZeroAccess, PornoBlocker, …](popular-ransomware.png)
