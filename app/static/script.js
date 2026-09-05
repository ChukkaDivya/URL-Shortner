function copyLink(customUrl) {
    let linkToCopy = customUrl;
    if (!linkToCopy) {
        const resultLink = document.querySelector(".result a");
        if (resultLink) {
            linkToCopy = resultLink.innerText;
        }
    }

    if (linkToCopy) {
        navigator.clipboard.writeText(linkToCopy).then(() => {
            alert("Copied!");
        }).catch(err => {
            console.error("Failed to copy link: ", err);
        });
    }
}

function checkAlias() {
    let aliasInput = document.getElementById("aliasInput");
    if (!aliasInput) return;

    let alias = aliasInput.value.replace(/[^a-zA-Z0-9_-]/g, "");

    let status = document.getElementById("aliasStatus");
    if (!status) return;

    if (alias.length < 2) {
        status.innerHTML = "";
        return;
    }

    fetch("/check-alias?alias=" + encodeURIComponent(alias))
        .then(res => res.json())
        .then(data => {
            if (data.available) {
                status.innerHTML = "<span style='color:green'>✓ Alias available</span>";
            } else {
                status.innerHTML = "<span style='color:red'>✗ Alias already taken or reserved</span>";
            }
        })
        .catch(err => {
            console.error("Error checking alias availability:", err);
        });
}

function togglePassword(inputId = "passwordInput", btnElement = null) {
    const input = document.getElementById(inputId);
    if (!input) return;

    if (input.type === "password") {
        input.type = "text";
        if (btnElement) {
            btnElement.textContent = "Hide";
        }
    } else {
        input.type = "password";
        if (btnElement) {
            btnElement.textContent = "Show";
        }
    }
}

function searchLinks() {
    let searchInput = document.getElementById("searchInput");
    if (!searchInput) return;

    let input = searchInput.value.toLowerCase();
    let rows = document.querySelectorAll("tbody tr");

    rows.forEach(row => {
        let text = row.innerText.toLowerCase();
        row.style.display = text.includes(input) ? "" : "none";
    });
}
