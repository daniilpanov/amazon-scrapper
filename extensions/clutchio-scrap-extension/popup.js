const grabBtn = document.getElementById("grabBtn");
grabBtn.addEventListener("click", () => {
    chrome.tabs.create({
        url: "https://clutch.co/agencies/ecommerce-marketing",
        active: false,
        autoDiscardable: false,
    }, function (tab) {
        chrome.runtime.sendMessage(tab.id);
    });
});
