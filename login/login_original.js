window.onload = () => {
	const code = location.href.substring(location.href.indexOf("code")+5, location.href.length)
	if (location.href.indexOf("code") > -1) {
		const data = new FormData();
    		data.append('client_id', ''); // insert bot client id
    		data.append('client_secret', ''); // insert bot client secret
    		data.append('grant_type', 'authorization_code');
    		data.append('redirect_uri', ""); // insert redirection URL
    		data.append('scope', 'identify');
    		data.append('code', code);

    		fetch('https://discordapp.com/api/oauth2/token', {
        		method: 'POST',
        		body: data,
    		})
        	.then(response => response.json())
        	.then(data=>{
            		const config = {
                		headers:{"authorization":`Bearer ${data.access_token}`}
            		}
            		axios.get("https://discordapp.com/api/users/@me",config)
                	.then(response=>{
                    		document.cookie = "id=" + response.data.id + ";Domain=.thestringharmony.com;Max-Age=31536000;Secure;Path=/" // change domain name
				document.getElementById("result").innerHTML = "Login successfully.<br />Close this window and start playing!"
                	})
                })
	}else{
		// change OAuth2 link
		window.location.replace("https://discord.com/api/oauth2/authorize?client_id=859512367480963103&redirect_uri=https%3A%2F%2Fthestringharmony.com%2Flogin&response_type=code&scope=identify")
	}
}