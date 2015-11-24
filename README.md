# passwm
Simple console password manager for Linux.
It stores all your passwords in a GPG encrypted file and allows to add, update
and delete individual entries.

## Installation
```bash
git clone https://github.com/aanatoly/passwm.git
cd passwm
make install # user install to ~/.local/bin
```

Make sure that `~/.local/bin` is in your `PATH`. Add this line to `~/.bashrc`
```bash
export PATH="$HOME/.local/bin:$PATH"
```

## Usage
Initialize `passwm` and add first entry (aka alias).
```
> passwm --init
Enter master password:
> passwm -a github
Enter master password: 
Enter the account name (username/email/etc): aanatoly
Enter password, or leave empty to generate random one:
```

List your aliases
```
> passwm -i all
Enter master password: 
alias 'github'
    username : aanatoly
    password : LZbUay2Hri4UWdhKQ6nK
     created : 2015-11-24 10:31:11
    modified : 2015-11-24 10:31:11
```



## Todo
Nice to have:

 * url as optional detail for an alias

## See also
Have a look at these console password managers

 * [bndw/pick](https://github.com/bndw/pick) - a minimalistic one
 * [thusoy/pwm](https://github.com/thusoy/pwm) - more features
