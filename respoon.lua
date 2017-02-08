hexchat.register('Respoon', '1', 'Automatic response manager')

hexchat.hook_server('PRIVMSG', function (args, args_eol)
	local autoresp = {}
	for id,arr in pairs(hexchat.pluginprefs) do
		local tline = split(arr, "\x01")
		table.insert(tline, 1, id)
		table.insert(autoresp, tline)
	end
	for _,arr in pairs(autoresp) do
		if args_eol[4] == ":"..arr[2] and (args[3] == arr[3] or arr[3] == "*") then
			hexchat.command('MSG '..args[3]..' '..arr[4]..'')
		end
	end
end)

hexchat.hook_command('RESPOON', function (args, args_eol)
	local badchars = {}
	for x in string.gmatch(args_eol[1], "\x01") do
		table.insert(badchars, x)
	end
	if #badchars > 0 then
		hexchat.print("Illegal character !")
	elseif args[2] == 'ADD' then
		if #args == 5 then
			local id = 1
			while hexchat.pluginprefs[id] ~= nil do
				id = id + 1
			end
			hexchat.pluginprefs[id] = args[3].."\x01"..args[4].."\x01"..args[5]
			hexchat.print("Respoon added (id "..id..")")
		else
			hexchat.print("Usage : RESPOON ADD <message> {*|#<channel>} <response>")
		end
	elseif args[2] == 'DEL' then
		if #args == 3 then
			hexchat.pluginprefs[tonumber(args[3])] = nil
			hexchat.print("Respoon removed (id "..args[3]..")")
		else
			hexchat.print("Usage : RESPOON DEL <ID>")
		end
	elseif args[2] == 'EDIT' then
		if #args == 6 then
			hexchat.pluginprefs[tonumber(args[3])] = args[4].."\x01"..args[5].."\x01"..args[6]
			hexchat.print("Respoon edited (id "..args[3]..")")
		else
			hexchat.print("Usage : RESPOON EDIT <ID> <message> {*|#<channel>|:<user>} <response>")
		end
	elseif args[2] == 'LIST' then
		if #args == 2 then
			PrintList(hexchat.pluginprefs)
		else
			hexchat.print("Usage : RESPOON LIST")
		end
	else
		hexchat.print("Usage : RESPOON {ADD|DEL|EDIT|LIST} [<params>]")
	end
	return hexchat.EAT_ALL
end)

function PrintList(list)
	local ltable = {}
	for id,arr in pairs(list) do
		local tline = split(arr, "\x01")
		table.insert(tline, 1, id)
		table.insert(ltable, tline)
	end
	local sizes = {2,7,7,8}
	for _,arr in pairs(ltable) do
		for i,v in pairs(sizes) do
			sizes[i] = math.max(string.len(arr[i]),sizes[i])
		end
	end
	local headers = {"ID", "Message", "Context", "Response"}
	local lne = "|"
	for i,v in pairs(sizes) do
		lne = lne.." "..headers[i]..string.rep(' ', v - string.len(headers[i])).." |"
	end
	hexchat.print(lne)
	lne = "|"
	for i,v in pairs(sizes) do
		lne = lne..string.rep('-', v + 2).."|"
	end
	hexchat.print(lne)
	for _,arr in pairs(ltable) do
		lne = "|"
		for i,v in pairs(sizes) do
			lne = lne.." "..arr[i]..string.rep(' ', v - string.len(arr[i])).." |"
		end
		hexchat.print(lne)
	end
end

function split(inputstr, sep)
        if sep == nil then
                sep = "%s"
        end
        local t={} ; i=1
        for str in string.gmatch(inputstr, "([^"..sep.."]+)") do
                t[i] = str
                i = i + 1
        end
        return t
end
