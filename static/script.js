function copyLink(){

let link = document.querySelector(".result a").innerText

navigator.clipboard.writeText(link)

alert("Copied!")
}

function checkAlias(){

let alias = document.getElementById("aliasInput").value

alias = alias.replace(/[^a-zA-Z0-9]/g,"")

if(alias.length < 2){
document.getElementById("aliasStatus").innerHTML = ""
return
}

fetch("/check-alias?alias=" + alias)
.then(res => res.json())
.then(data => {

let status = document.getElementById("aliasStatus")

if(data.available){
status.innerHTML =
"<span style='color:green'>✓ Alias available</span>"
}
else{
status.innerHTML =
"<span style='color:red'>✗ Alias already taken</span>"
}

})

}


function togglePassword(){

let input = document.getElementById("passwordInput")

if(input.type === "password"){
input.type = "text"
}else{
input.type = "password"
}

}