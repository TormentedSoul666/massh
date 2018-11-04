# massh

Mass SSH bruteforce/credential testing

## Why did I make this?

Long story short, I was always having problems `hydra`'s file limit of 500000 bytes, and since I didn't really need anything but SSH from it, I wrote this.

It's a slimmed down version of [Shodan-RPi](https://github.com/btx3/Shodan-RPi) - without Shodan support.

## Setup

```
apt install libssl-dev python3-pip # or the equivalent for your OS
pip3 install -r requirements.txt
```

## Usage

`./massh.py -u oracle -p oracle -i servers.txt` - Test which servers in `servers.txt` respond to `oracle:oracle`.

`./massh.py -u john -ssh-key id_rsa -i servers.txt -c hostname` - Test ssh-key `id_rsa` with username `john` on all servers in `servers.txt`, and if the authentication succeeds, execute `hostname`.

## Bugs

There is supposed to be a hosts-processed counter and success counter but I didn't want to deal with that (also doubt that anyone needs it right now).

When using `-ssh-key`, just add a random letter as a password (like `-ssh-key id_rsa -p a`), I haven't yet set up mutually-exclusive argument parsing for these arguments.

The code isn't really too documented, I'll try to do that in the next couple months.

Not really a bug, but try to be reasonable when setting the thread count - you might end up with an unresponsive machine.

Probably more but I haven't tested much.
