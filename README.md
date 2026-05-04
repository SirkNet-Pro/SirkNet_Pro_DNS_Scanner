$ python SirkNet.py

```
╭──────────────────────────────────────────╮
│ SirkNet_Pro_DNS                          │
│ Developed by APT IRAN                    │
│                                          │
│ Telegram: https://t.me/+6EzmY-eAkLFkZWYy │
╰──────────────────────────────────────────╯
Enter IP list file: ips2.txt
Enter output file: valid3.txt
Enter test domain: telegram.org

Loaded 91 IPs
Domain: telegram.org
        Phase 1 - Quick Check
┏━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Processed ┃ Passed ┃ Speed (IP/s) ┃
┡━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━┩
│   91/91   │   71   │     27.0     │
└───────────┴────────┴──────────────┘
[✓] Phase 1 - Quick Check finished | Passed: 71
        Phase 2 - Large Query
┏━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Processed ┃ Passed ┃ Speed (IP/s) ┃
┡━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━┩
│   71/71   │   6    │     9.8      │
└───────────┴────────┴──────────────┘
[✓] Phase 2 - Large Query finished | Passed: 6

Phase 3 - Stability Test
VALID 217.218.155.155 | 161.2ms
VALID 2.189.44.44 | 161.2ms
               Phase 3
┏━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Processed ┃ Passed ┃ Speed (IP/s) ┃
┡━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━┩
│    6/6    │   2    │     6.0      │
└───────────┴────────┴──────────────┘
╭──────────────────────╮
│ Finished             │
│ Valid IPs: 2         │
│ Saved in: valid3.txt │
╰──────────────────────╯
```
