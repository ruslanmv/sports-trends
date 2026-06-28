/* sports-share.js — share buttons (native share, X/WhatsApp intents, copy). */
(function () {
  "use strict";
  function _base(){var m=document.querySelector('meta[name="sports-base"]');return (m?m.content:"/").replace(/\/$/,"");}
  function matchUrl(id) { return location.origin + _base() + "/sports/match/" + id + "/"; }

  document.addEventListener("click", function (event) {
    var shareBtn = event.target.closest("[data-share-match]");
    if (shareBtn) {
      var url = matchUrl(shareBtn.dataset.shareMatch);
      if (navigator.share) { navigator.share({ title: "Ruslan Magana Sports Intelligence", url: url }).catch(function () {}); }
      else if (navigator.clipboard) { navigator.clipboard.writeText(url); shareBtn.textContent = "Copied"; }
      return;
    }
    var net = event.target.closest("[data-share]");
    if (!net) return;
    var pageUrl = location.href;
    var text = document.title;
    var targets = {
      x: "https://twitter.com/intent/tweet?text=" + encodeURIComponent(text) + "&url=" + encodeURIComponent(pageUrl),
      whatsapp: "https://wa.me/?text=" + encodeURIComponent(text + " " + pageUrl)
    };
    var kind = net.dataset.share;
    if (kind === "copy" && navigator.clipboard) { navigator.clipboard.writeText(pageUrl); net.textContent = "Copied"; }
    else if (targets[kind]) { window.open(targets[kind], "_blank", "noopener"); }
  });
})();
