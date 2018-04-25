# Respoon
Automatic response manager addon for Hexchat

## Usage

Add an automatic response :
`/RESPOON ADD <name> <server> <channel> "<trigger>" MSG|CMD <action>`

List every automatic responses :
`/RESPOON LIST`

Show properties of a specific response :
`/RESPOON SHOW <name>`

Edit an automatic reponse :
`/RESPOON EDIT <name> <server> <channel> "<trigger>" MSG|CMD <action>`

Remove an automatic reponses :
`/RESPOON DELETE <name>`


Property `<trigger>` is in regex format. Keep double-quote around if the regex contains spaces.

You can use those escape sequences in the `<action>` property :
* {user} : the nick of the user
* {message} : the full message that has been sent
* {server} : the server where the message has been sent
* {channel} : the channel where the message has been sent
* {params\[x\]} : the match of your regex at index 'x'
			
## Examples

`/RESPOON ADD hello_resp *.worldnet.net #mychannel ^Hello.+$ MSG Welcome {user} !`

`/RESPOON ADD eat_muffin * * "^Who wants a muffin ?$" CMD ME eat the muffin !`

`/RESPOON EDIT eat_muffin * * "^Who wants a (.+) ?$" CMD ME eat the {params[0]} !`

`/RESPOON DELETE eat_muffin`
