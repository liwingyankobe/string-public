// put this js in all pages where you want to trigger the bot
function readCookie(name) {
	var nameEQ = name + "=";
	var ca = document.cookie.split(';');
	for(var i=0;i < ca.length;i++) {
		var c = ca[i];
		while (c.charAt(0)==' ') c = c.substring(1,c.length);
		if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
	}
	return null;
}

window.onload = () => {
	const did = readCookie('id')
	if (did != null) {
		const path = window.location.pathname
		const uri = '' // insert bot interaction URL e.g. https://the-string-harmony-bot.herokuapp.com/
		const data = {id: did, ans: path}
		fetch(uri, {
  			method: 'POST',
  			headers: {
    				'Content-Type': 'application/json',
  			},
  			body: JSON.stringify(data),
		})
		.then(response => {})
	}
}
	