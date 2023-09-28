var $jscomp = $jscomp || {};
$jscomp.scope = {};
$jscomp.checkStringArgs = function(g, q, f) {
  if (null == g) {
    throw new TypeError("The 'this' value for String.prototype." + f + " must not be null or undefined");
  }
  if (q instanceof RegExp) {
    throw new TypeError("First argument to String.prototype." + f + " must not be a regular expression");
  }
  return g + "";
};
$jscomp.ASSUME_ES5 = !1;
$jscomp.ASSUME_NO_NATIVE_MAP = !1;
$jscomp.ASSUME_NO_NATIVE_SET = !1;
$jscomp.SIMPLE_FROUND_POLYFILL = !1;
$jscomp.defineProperty = $jscomp.ASSUME_ES5 || "function" == typeof Object.defineProperties ? Object.defineProperty : function(g, q, f) {
  g != Array.prototype && g != Object.prototype && (g[q] = f.value);
};
$jscomp.getGlobal = function(g) {
  return "undefined" != typeof window && window === g ? g : "undefined" != typeof global && null != global ? global : g;
};
$jscomp.global = $jscomp.getGlobal(this);
$jscomp.polyfill = function(g, q, f, u) {
  if (q) {
    f = $jscomp.global;
    g = g.split(".");
    for (u = 0; u < g.length - 1; u++) {
      var k = g[u];
      k in f || (f[k] = {});
      f = f[k];
    }
    g = g[g.length - 1];
    u = f[g];
    q = q(u);
    q != u && null != q && $jscomp.defineProperty(f, g, {configurable:!0, writable:!0, value:q});
  }
};
$jscomp.polyfill("String.prototype.startsWith", function(g) {
  return g ? g : function(g, f) {
    var q = $jscomp.checkStringArgs(this, g, "startsWith");
    g += "";
    var k = q.length, y = g.length;
    f = Math.max(0, Math.min(f | 0, q.length));
    for (var E = 0; E < y && f < k;) {
      if (q[f++] != g[E++]) {
        return !1;
      }
    }
    return E >= y;
  };
}, "es6", "es3");
$jscomp.polyfill("String.prototype.endsWith", function(g) {
  return g ? g : function(g, f) {
    var q = $jscomp.checkStringArgs(this, g, "endsWith");
    g += "";
    void 0 === f && (f = q.length);
    f = Math.max(0, Math.min(f | 0, q.length));
    for (var k = g.length; 0 < k && 0 < f;) {
      if (q[--f] != g[--k]) {
        return !1;
      }
    }
    return 0 >= k;
  };
}, "es6", "es3");
$jscomp.findInternal = function(g, q, f) {
  g instanceof String && (g = String(g));
  for (var u = g.length, k = 0; k < u; k++) {
    var y = g[k];
    if (q.call(f, y, k, g)) {
      return {i:k, v:y};
    }
  }
  return {i:-1, v:void 0};
};
$jscomp.polyfill("Array.prototype.find", function(g) {
  return g ? g : function(g, f) {
    return $jscomp.findInternal(this, g, f).v;
  };
}, "es6", "es3");
(function() {
  var g = window, q = !1;
  String.prototype.hashCode = function() {
    var a = 0, c;
    if (0 === this.length) {
      return a;
    }
    var e = 0;
    for (c = this.length; e < c; e++) {
      var b = this.charCodeAt(e);
      a = (a << 5) - a + b;
      a |= 0;
    }
    return a;
  };
  var f = "optOut_crawl revealStock s_boxOfferListing s_boxType s_boxHorizontal webGraphType webGraphRange overlayPriceGraph".split(" "), u = window.opera || -1 < navigator.userAgent.indexOf(" OPR/"), k = -1 < navigator.userAgent.toLowerCase().indexOf("firefox"), y = -1 < navigator.userAgent.toLowerCase().indexOf("edge/"), E = /Apple Computer/.test(navigator.vendor) && /Safari/.test(navigator.userAgent), F = !u && !k && !y && !E, N = F ? "keepaChrome" : u ? "keepaOpera" : E ? "keepaSafari" : y ? 
  "keepaEdge" : "keepaFirefox", Z = k ? "Firefox" : E ? "Safari" : F ? "Chrome" : u ? "Opera" : y ? "Edge" : "Unknown", C = null, H = !1;
  try {
    H = /Android|webOS|iPhone|iPad|iPod|BlackBerry/i.test(navigator.userAgent);
  } catch (a) {
  }
  if (F) {
    try {
      chrome.runtime.sendMessage("hnkcfpcejkafcihlgbojoidoihckciin", {type:"isActive"}, null, function(a) {
        chrome.runtime.lastError || a && a.isActive && (q = !0);
      });
    } catch (a) {
    }
  }
  try {
    chrome.runtime.onUpdateAvailable.addListener(function(a) {
      chrome.runtime.reload();
    });
  } catch (a) {
  }
  var O = {}, Q = 0;
  chrome.runtime.onMessage.addListener(function(a, d, e) {
    if (d.tab && d.tab.url || d.url) {
      switch(a.type) {
        case "restart":
          document.location.reload(!1);
          break;
        case "setCookie":
          chrome.cookies.set({url:"https://keepa.com", path:"/extension", name:a.key, value:a.val, secure:!0, expirationDate:(Date.now() / 1000 | 0) + 31536E3});
          "token" == a.key ? C != a.val && 64 == a.val.length && (C = a.val, c.set("token", C), setTimeout(function() {
            document.location.reload(!1);
          }, 300)) : c.set(a.key, a.val);
          break;
        case "getCookie":
          return chrome.cookies.get({url:"https://keepa.com/extension", name:a.key}, function(a) {
            null == a ? e({value:null}) : e({value:a.value});
          }), !0;
        case "openPage":
          chrome.windows.create({url:a.url, incognito:!0});
          break;
        case "isPro":
          c.stockData ? e({value:c.stockData.pro, stockData:c.stockData}) : e({value:null});
          break;
        case "getStock":
          return c.addStockJob(a, function(b) {
            0 < b.errorCode && a.cachedStock ? e(a.cachedStock) : 5 == b.errorCode || 429 == b.errorCode || 9 == b.errorCode ? (9 == b.errorCode && (a.getNewId = !0), setTimeout(function() {
              c.addStockJob(a, e);
            }, 1)) : e(b);
          }), !0;
        case "getFilters":
          e({value:t.getFilters()});
          break;
        case "sendData":
          d = a.val;
          if (null != d.ratings) {
            var b = d.ratings;
            if (1000 > Q) {
              if ("f1" == d.key) {
                if (b) {
                  for (var v = b.length; v--;) {
                    var h = b[v];
                    null == h || null == h.asin ? b.splice(v, 1) : (h = d.domainId + h.asin + h.ls, O[h] ? b.splice(v, 1) : (O[h] = 1, Q++));
                  }
                  0 < b.length && p.sendPlainMessage(d);
                }
              } else {
                p.sendPlainMessage(d);
              }
            } else {
              O = null;
            }
          } else {
            p.sendPlainMessage(d);
          }
          e({});
          break;
        case "optionalPermissionsRequired":
          e({value:(F || k || u) && "undefined" === typeof chrome.webRequest});
          break;
        case "optionalPermissionsDenied":
          c.set("optOut_crawl", "1");
          console.log("optionalPermissionsDenied");
          e({value:!0});
          break;
        case "optionalPermissionsInContent":
          d = a.val;
          "undefined" != typeof d && (d ? (c.set("optOut_crawl", "0"), console.log("granted"), chrome.runtime.reload()) : (c.set("optOut_crawl", "1"), l.reportBug("permission denied"), console.log("denied")));
          e({value:!0});
          break;
        case "optionalPermissions":
          return "undefined" === typeof chrome.webRequest && chrome.permissions.request({permissions:["webRequest", "webRequestBlocking"]}, function(a) {
            chrome.runtime.lastError || (e({value:a}), "undefined" != typeof a && (a ? (c.set("optOut_crawl", "0"), console.log("granted"), chrome.runtime.reload()) : (c.set("optOut_crawl", "1"), l.reportBug("permission denied"), console.log("denied"))));
          }), !0;
        default:
          e({});
      }
    }
  });
  window.onload = function() {
    k ? chrome.storage.local.get(["install", "optOutCookies"], function(a) {
      a.optOutCookies && 3456E5 > Date.now() - a.optOutCookies || (a.install ? l.register() : chrome.tabs.create({url:chrome.runtime.getURL("chrome/content/onboard.html")}));
    }) : l.register();
  };
  try {
    chrome.browserAction.onClicked.addListener(function(a) {
      c.isGuest ? chrome.tabs.create({url:c.actionUrl}) : chrome.tabs.create({url:"https://keepa.com/#!manage"});
    });
  } catch (a) {
    console.log(a);
  }
  var c = {storage:chrome.storage.local, contextMenu:function() {
    try {
      chrome.contextMenus.removeAll(), chrome.contextMenus.create({title:"View products on Keepa", contexts:["page"], id:"keepaContext", documentUrlPatterns:"*://*.amazon.com/* *://*.amzn.com/* *://*.amazon.co.uk/* *://*.amazon.de/* *://*.amazon.fr/* *://*.amazon.it/* *://*.amazon.ca/* *://*.amazon.com.mx/* *://*.amazon.es/* *://*.amazon.co.jp/* *://*.amazon.in/*".split(" ")}), chrome.contextMenus.onClicked.addListener(function(a, c) {
        chrome.tabs.sendMessage(c.id, {key:"collectASINs"}, {}, function(a) {
          "undefined" != typeof a && chrome.tabs.create({url:"https://keepa.com/#!viewer/" + encodeURIComponent(JSON.stringify(a))});
        });
      });
    } catch (a) {
      console.log(a);
    }
  }, parseCookieHeader:function(a, c) {
    if (0 < c.indexOf("\n")) {
      c = c.split("\n");
      var e = 0;
      a: for (; e < c.length; ++e) {
        var b = c[e].substring(0, c[e].indexOf(";")), v = b.indexOf("=");
        b = [b.substring(0, v), b.substring(v + 1)];
        if (2 == b.length && "-" != b[1]) {
          for (v = 0; v < a.length; ++v) {
            if (a[v][0] == b[0]) {
              a[v][1] = b[1];
              continue a;
            }
          }
          a.push(b);
        }
      }
    } else {
      if (c = c.substring(0, c.indexOf(";")), e = c.indexOf("="), c = [c.substring(0, e), c.substring(e + 1)], 2 == c.length && "-" != c[1]) {
        for (e = 0; e < a.length; ++e) {
          if (a[e][0] == c[0]) {
            a[e][1] = c[1];
            return;
          }
        }
        a.push(c);
      }
    }
  }, log:function(a) {
    l.quiet || console.log(a);
  }, iframeWin:null, operationComplete:!1, counter:0, stockInit:!1, stockRequest:[], initStock:function() {
    if (!c.stockInit && "undefined" != typeof chrome.webRequest) {
      var a = ["xmlhttprequest"], d = "*://www.amazon.com/* *://www.amazon.co.uk/* *://www.amazon.es/* *://www.amazon.nl/* *://www.amazon.com.mx/* *://www.amazon.it/* *://www.amazon.in/* *://www.amazon.de/* *://www.amazon.fr/* *://www.amazon.co.jp/* *://www.amazon.ca/* *://www.amazon.com.br/* *://www.amazon.com.au/* *://www.amazon.com.mx/* *://smile.amazon.com/* *://smile.amazon.co.uk/* *://smile.amazon.es/* *://smile.amazon.nl/* *://smile.amazon.com.mx/* *://smile.amazon.it/* *://smile.amazon.in/* *://smile.amazon.de/* *://smile.amazon.fr/* *://smile.amazon.co.jp/* *://smile.amazon.ca/* *://smile.amazon.com.br/* *://smile.amazon.com.au/* *://smile.amazon.com.mx/*".split(" ");
      try {
        var e = [c.stockData.addCartHeaders, c.stockData.geoHeaders, c.stockData.setAddressHeaders, c.stockData.addressChangeHeaders, c.stockData.productPageHeaders, c.stockData.toasterHeaders];
        chrome.webRequest.onBeforeSendHeaders.addListener(function(a) {
          if (a.initiator) {
            if (a.initiator.startsWith("http")) {
              return;
            }
          } else {
            if (a.originUrl && !a.originUrl.startsWith("moz-extension")) {
              return;
            }
          }
          var b = a.requestHeaders, h = {};
          try {
            for (var d = null, g = 0; g < b.length; ++g) {
              if ("krequestid" == b[g].name) {
                d = b[g].value;
                b.splice(g--, 1);
                break;
              }
            }
            if (d) {
              var l = c.stockRequest[d];
              c.stockRequest[a.requestId] = l;
              setTimeout(function() {
                delete c.stockRequest[a.requestId];
              }, 30000);
              var f = e[l.requestType];
              for (d = 0; d < b.length; ++d) {
                var q = b[d].name.toLowerCase();
                (f[q] || "" === f[q] || f[b[d].name] || "cookie" == q || "content-type" == q || "sec-fetch-dest" == q || "sec-fetch-mode" == q || "sec-fetch-user" == q || "accept" == q || "referer" == q) && b.splice(d--, 1);
              }
              if (0 == l.requestType && 19 > l.stockSession.length) {
                return h.cancel = !0, h;
              }
              var n = c.stockData.isMobile ? "https://" + l.host + "/gp/aw/d/" + l.asin + "/" : l.referer, k;
              for (k in f) {
                var p = f[k];
                if (0 != p.length) {
                  p = p.replace("{COOKIE}", l.stockSession).replace("{REFERER}", n).replace("{ORIGIN}", l.host);
                  if (-1 < p.indexOf("{CSRF}")) {
                    if (l.csrf) {
                      p = p.replace("{CSRF}", l.csrf), l.csrf = null;
                    } else {
                      continue;
                    }
                  }
                  b.push({name:k, value:p});
                }
              }
              for (f = 0; f < b.length; ++f) {
                var t = b[f].name.toLowerCase();
                (c.stockData.stockHeaders[t] || "" === c.stockData.stockHeaders[t] || c.stockData.stockHeaders[b[f].name] || "origin" == t || "pragma" == t || "cache-control" == t || "upgrade-insecure-requests" == t) && b.splice(f--, 1);
              }
              for (var K in c.stockData.stockHeaders) {
                var u = c.stockData.stockHeaders[K];
                0 != u.length && (u = u.replace("{COOKIE}", l.stockSession).replace("{REFERER}", n).replace("{ORIGIN}", l.host).replace("{LANG}", c.stockData.languageCode[l.domainId]), b.push({name:K, value:u}));
              }
              h.requestHeaders = b;
              a.requestHeaders = b;
            } else {
              return h;
            }
          } catch (I) {
            h.cancel = !0;
          }
          return h;
        }, {urls:d, types:a}, F ? ["blocking", "requestHeaders", "extraHeaders"] : ["blocking", "requestHeaders"]);
        chrome.webRequest.onHeadersReceived.addListener(function(a) {
          if (a.initiator) {
            if (a.initiator.startsWith("http")) {
              return;
            }
          } else {
            if (a.originUrl && !a.originUrl.startsWith("moz-extension")) {
              return;
            }
          }
          var b = a.responseHeaders, e = {};
          try {
            var d = c.stockRequest[a.requestId];
            if (d) {
              var g = d.cookies || [];
              for (a = 0; a < b.length; ++a) {
                "set-cookie" == b[a].name.toLowerCase() && (c.parseCookieHeader(g, b[a].value), b.splice(a, 1), a--);
              }
              d.cookies = g;
              switch(d.requestType) {
                case 0:
                case 1:
                case 2:
                case 4:
                case 5:
                  e.responseHeaders = b;
                  break;
                case 3:
                  e.cancel = !0, setTimeout(function() {
                    d.cookies = g;
                    c.stockSessions[d.domainId] = g;
                    d.callback();
                  }, 10);
              }
              if (0 != d.requestType) {
                b = "";
                for (a = 0; a < d.cookies.length; ++a) {
                  var l = d.cookies[a];
                  b += l[0] + "=" + l[1] + "; ";
                  "session-id" == l[0] && 16 < l[1].length && 65 > l[1].length && l[1] != d.session && (d.sessionIdMismatch = !0);
                }
                d.stockSession = b;
              }
            } else {
              return e;
            }
          } catch (aa) {
            e.cancel = !0;
          }
          return e;
        }, {urls:d, types:a}, F ? ["blocking", "responseHeaders", "extraHeaders"] : ["blocking", "responseHeaders"]);
        c.stockInit = !0;
      } catch (b) {
        l.reportBug(b, b.message + " stock exception: " + typeof chrome.webRequest + " " + ("undefined" != typeof chrome.webRequest ? typeof chrome.webRequest.onBeforeSendHeaders : "~") + " " + ("undefined" != typeof chrome.webRequest ? typeof chrome.webRequest.onHeadersReceived : "#"));
      }
    }
  }, stockData:null, isGuest:!0, actionUrl:"https://keepa.com/#!features", stockJobQueue:[], stockSessions:[], addStockJob:function(a, d) {
    a.gid = l.Guid.newGuid().substr(0, 8);
    a.requestType = -1;
    c.stockRequest[a.gid] = a;
    var e = function(a) {
      c.stockJobQueue.shift();
      d(a);
      0 < c.stockJobQueue.length && c.processStockJob(c.stockJobQueue[0][0], c.stockJobQueue[0][1]);
    };
    c.stockJobQueue.push([a, e]);
    1 == c.stockJobQueue.length && c.processStockJob(a, e);
  }, processStockJob:function(a, d) {
    if (null == c.stockData.stock) {
      console.log("stock retrieval not initialized"), d({error:"stock retrieval not initialized", errorCode:0});
    } else {
      if (0 == c.stockData.stockEnabled[a.domainId]) {
        console.log("stock retrieval not supported for domain"), d({error:"stock retrieval not supported for domain", errorCode:1});
      } else {
        if (!0 === c.stockData.pro || a.force) {
          if (a.maxQty) {
            if (!a.isMAP && c.stockData.stockMaxQty && a.maxQty < c.stockData.stockMaxQty) {
              d({stock:a.maxQty, limit:!1});
              return;
            }
            console.log("set backup stock maxQty: " + a.maxQty);
            a.cachedStock = {stock:a.maxQty, limit:!1, isMaxQty:a.maxQty};
          }
          null == a.oid ? (console.log("missing oid", a), d({error:"stock retrieval failed for offer: " + a.asin + " id: " + a.gid + " missing oid.", errorCode:12})) : a.onlyMaxQty && !a.isMAP ? d() : (c.initStock(), setTimeout(function() {
            if (c.stockInit) {
              if (setTimeout(function() {
                delete c.stockSessions[a.domainId];
              }, 36E5), setTimeout(function() {
                delete c.stockRequest[a.gid];
              }, 3E5), a.queue = [function() {
                for (var b = "", e = !1, h = !1, g = 0, f = 0; f < a.cookies.length; ++f) {
                  var q = a.cookies[f];
                  b += q[0] + "=" + q[1] + "; ";
                  "session-id" == q[0] && 16 < q[1].length && 65 > q[1].length && (e = !0, q[1] != a.session && (h = !0, g = q[1]));
                }
                a.cookie = b;
                e && h ? (a.stockSession = b, b = c.stockData.addCartUrl, e = c.stockData.addCartPOST, a.requestType = 0, l.httpPost("https://" + a.host + b.replaceAll("{SESSION_ID}", g).replaceAll("{OFFER_ID}", a.oid).replaceAll("{ADDCART}", c.stockData.stockAdd[a.domainId]).replaceAll("{ASIN}", a.asin), e.replaceAll("{SESSION_ID}", g).replaceAll("{OFFER_ID}", a.oid).replaceAll("{ADDCART}", c.stockData.stockAdd[a.domainId]).replaceAll("{ASIN}", a.asin), function(b) {
                  var e = decodeURIComponent(a.oid).replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), h = b.match(new RegExp(c.stockData.stock)), v = b.match(new RegExp(c.stockData.stockAlt)), g = b.match(new RegExp(c.stockData.stockAlt2.replaceAll("{ESCAPED_OID}", e))), l = b.match(new RegExp(c.stockData.price)), f = b.match(new RegExp(c.stockData.priceSingle.replaceAll("{ESCAPED_OID}", e)));
                  e = (new RegExp(c.stockData.limit)).test(b);
                  null == h && (h = g);
                  if (h && h[1]) {
                    b = parseInt(h[1]), h = -1, v && v[1] && (h = parseInt(v[1])), g && g[1] && (h = parseInt(g[1])), v = -1, f && 1 < f.length ? (f[1].lastIndexOf(".") == f[1].length - 2 && (f[1] += "0"), v = parseInt(f[1].replace(/[\D]/g, ""))) : l && (v = parseInt(l[1].replace(/[\D]/g, "")) / b), l = -1, 0 < h && 100 > h && b > h && (e = !0, l = h), d({stock:Math.max(b, h), orderLimit:l, limit:e, price:v});
                  } else {
                    if ((l = b.match(/automated access|api-services-support@/)) || a.isRetry) {
                      delete c.stockSessions[a.domainId], a.cookie = null, a.stockSession = null, a.cookies = null;
                    }
                    l ? (d({error:"Amazon stock retrieval rate limited (bot detection) of offer: " + a.asin + " id: " + a.gid + " offer: " + a.oid, errorCode:5}), console.log("stock retrieval rate limited for offer: ", a.asin + " " + a.oid + " id: " + a.gid, b.length)) : d({error:"Stock retrieval failed for this offer. Try reloading the page after a while. ", errorCode:9});
                  }
                }, !1, a.gid)) : (l.reportBug(null, "stock session issue: " + e + " " + h + " counter: " + c.counter + " c: " + JSON.stringify(a.cookies) + " " + JSON.stringify(a)), d({error:"stock session issue: " + e + " " + h, errorCode:4}));
              }], a.getNewId && (c.stockData.geoRetry && delete c.stockSessions[a.domainId], a.queue.unshift(function() {
                a.requestType = 4;
                l.httpGet("https://" + c.stockData.offerUrl.replace("{ORIGIN}", a.host).replace("{ASIN}", a.asin).replace("{SID}", a.sellerId), function(b) {
                  if (b.match(c.stockData.sellerIdBBVerify.replace("{SID}", a.sellerId))) {
                    for (var e = null, h = 0; h < c.stockData.csrfBB.length; h++) {
                      var g = b.match(new RegExp(c.stockData.csrfBB[h]));
                      if (null != g && g[1]) {
                        e = g[1];
                        break;
                      }
                    }
                    if (e) {
                      a.csrf = e[1];
                      e = null;
                      for (h = 0; h < c.stockData.offerIdBB.length; h++) {
                        if (g = b.match(new RegExp(c.stockData.offerIdBB[h])), null != g && g[1]) {
                          e = g[1];
                          break;
                        }
                      }
                      e && (a.oid = e, a.callback());
                    }
                  } else {
                    d({error:"stock retrieval failed for offer: " + a.asin + " id: " + a.gid + " mismatch oid.", errorCode:10});
                  }
                }, !1, a.gid);
              })), a.callback = function() {
                return a.queue.shift()();
              }, c.stockSessions[a.domainId]) {
                a.cookies = c.stockSessions[a.domainId], a.callback();
              } else {
                var e = c.stockData.zipCodes[a.domainId];
                c.stockData.domainId == a.domainId ? (a.requestType = 3, l.httpPost("https://" + a.host + c.stockData.addressChangeUrl, c.stockData.addressChangePOST.replace("{ZIPCODE}", e), null, !1, a.gid)) : (a.requestType = 1, l.httpGet("https://" + a.host + c.stockData.geoUrl, function(b, g) {
                  b = b.match(new RegExp(c.stockData.csrfGeo));
                  if (null != b) {
                    a.csrf = b[1], a.requestType = 5, l.httpGet("https://" + a.host + c.stockData.toasterUrl.replace("{TIME_MS}", Date.now()), function(b) {
                      a.requestType = 2;
                      l.httpGet("https://" + a.host + c.stockData.setAddressUrl, function(b) {
                        b = b.match(new RegExp(c.stockData.csrfSetAddress));
                        null != b && (a.csrf = b[1]);
                        a.requestType = 3;
                        l.httpPost("https://" + a.host + c.stockData.addressChangeUrl, c.stockData.addressChangePOST.replace("{ZIPCODE}", e), null, !1, a.gid);
                      }, !1, a.gid);
                    }, !1, a.gid);
                  } else {
                    if (429 == g) {
                      var h = a.isMainRetry;
                      setTimeout(function() {
                        h ? d({error:"stock retrieval failed for offer: " + a.asin + " id: " + a.gid + " main.", errorCode:429}) : (a.isMainRetry = !0, c.addStockJob(a, d));
                      }, 1156);
                      h || (c.stockJobQueue.shift(), 0 < c.stockJobQueue.length && c.processStockJob(c.stockJobQueue[0][0], c.stockJobQueue[0][1]));
                    } else {
                      d({error:"stock retrieval failed for offer: " + a.asin + " id: " + a.gid + " main.", errorCode:7});
                    }
                  }
                }, !1, a.gid));
              }
            } else {
              console.log("could not init stock retrieval", c.stockInit, typeof chrome.webRequest), d({error:"could not init stock retrieval", errorCode:"undefined" != typeof chrome.webRequest ? 3 : 33});
            }
          }, 20));
        } else {
          console.log("stock retrieval not pro"), d({error:"stock retrieval failed, not subscribed", errorCode:2});
        }
      }
    }
  }, set:function(a, d, e) {
    var b = {};
    b[a] = d;
    c.storage.set(b, e);
  }, remove:function(a, d) {
    c.storage.remove(a, d);
  }, get:function(a, d) {
    "function" != typeof d && (d = function() {
    });
    c.storage.get(a, function(a) {
      d(a);
    });
  }};
  c.contextMenu();
  var l = {quiet:!0, version:chrome.runtime.getManifest().version, browser:1, url:"https://keepa.com", testUrl:"https://test.keepa.com", getDomain:function(a) {
    switch(a) {
      case "com":
        return 1;
      case "co.uk":
        return 2;
      case "de":
        return 3;
      case "fr":
        return 4;
      case "co.jp":
        return 5;
      case "ca":
        return 6;
      case "it":
        return 8;
      case "es":
        return 9;
      case "in":
        return 10;
      case "com.mx":
        return 11;
      case "com.br":
        return 12;
      case "com.au":
        return 13;
      case "nl":
        return 14;
      default:
        return 1;
    }
  }, objectStorage:[], Guid:function() {
    var a = function(c, b, d) {
      return c.length >= b ? c : a(d + c, b, d || " ");
    }, c = function() {
      var a = (new Date).getTime();
      return "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx".replace(/x/g, function(c) {
        var b = (a + 16 * Math.random()) % 16 | 0;
        a = Math.floor(a / 16);
        return ("x" === c ? b : b & 7 | 8).toString(16);
      });
    };
    return {newGuid:function() {
      var e = "undefined" != typeof window.crypto.getRandomValues;
      if ("undefined" != typeof window.crypto && e) {
        e = new window.Uint16Array(16);
        window.crypto.getRandomValues(e);
        var b = "";
        for (h in e) {
          var d = e[h].toString(16);
          d = a(d, 4, "0");
          b += d;
        }
        var h = b;
      } else {
        h = c();
      }
      return h;
    }};
  }(), register:function() {
    chrome.cookies.onChanged.addListener(function(a) {
      a.removed || null == a.cookie || "keepa.com" != a.cookie.domain || "/extension" != a.cookie.path || ("token" == a.cookie.name ? C != a.cookie.value && 64 == a.cookie.value.length && (C = a.cookie.value, c.set("token", C), setTimeout(function() {
        document.location.reload(!1);
      }, 300)) : c.set(a.cookie.name, a.cookie.value));
    });
    var a = !1, d = function(e) {
      for (var b = {}, d = 0; d < e.length; b = {$jscomp$loop$prop$name$70:b.$jscomp$loop$prop$name$70}, d++) {
        b.$jscomp$loop$prop$name$70 = e[d];
        try {
          chrome.cookies.get({url:"https://keepa.com/extension", name:b.$jscomp$loop$prop$name$70}, function(b) {
            return function(e) {
              chrome.runtime.lastError && -1 < chrome.runtime.lastError.message.indexOf("No host permission") ? a || (a = !0, l.reportBug("extensionPermission restricted ### " + chrome.runtime.lastError.message)) : null != e && null != e.value && 0 < e.value.length && c.set(b.$jscomp$loop$prop$name$70, e.value);
            };
          }(b));
        } catch (h) {
          console.log(h);
        }
      }
    };
    d(f);
    chrome.cookies.get({url:"https://keepa.com/extension", name:"token"}, function(a) {
      if (null != a && 64 == a.value.length) {
        C = a.value, c.set("token", C);
      } else {
        var b = (Date.now() / 1000 | 0) + 31536E3;
        chrome.cookies.set({url:"https://keepa.com", path:"/extension", name:"optOut_crawl", value:"0", secure:!0, expirationDate:b});
        chrome.cookies.set({url:"https://keepa.com", path:"/extension", name:"revealStock", value:"1", secure:!0, expirationDate:b});
        chrome.cookies.set({url:"https://keepa.com", path:"/extension", name:"s_boxType", value:"0", secure:!0, expirationDate:b});
        chrome.cookies.set({url:"https://keepa.com", path:"/extension", name:"s_boxOfferListing", value:"1", secure:!0, expirationDate:b});
        chrome.cookies.set({url:"https://keepa.com", path:"/extension", name:"s_boxHorizontal", value:"0", secure:!0, expirationDate:b});
        chrome.cookies.set({url:"https://keepa.com", path:"/extension", name:"webGraphType", value:"[1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]", secure:!0, expirationDate:b});
        chrome.cookies.set({url:"https://keepa.com", path:"/extension", name:"webGraphRange", value:"180", secure:!0, expirationDate:b});
        chrome.cookies.set({url:"https://keepa.com", path:"/extension", name:"overlayPriceGraph", value:"0", secure:!0, expirationDate:b});
        d(f);
        c.get("token", function(a) {
          C = (a = a.token) && 64 == a.length ? a : l.Guid.newGuid();
          chrome.cookies.set({url:"https://keepa.com", path:"/extension", name:"token", value:C, secure:!0, expirationDate:b});
        });
      }
    });
    try {
      "undefined" != typeof chrome.storage.sync && chrome.storage.sync.clear();
    } catch (e) {
    }
    window.addEventListener("message", function(a) {
      var c = a.data;
      if (c) {
        if ("string" === typeof c) {
          try {
            c = JSON.parse(c);
          } catch (W) {
            return;
          }
        }
        if (c.log) {
          console.log(c.log);
        } else {
          var e = function() {
          };
          if (a.origin != l.url && a.origin != l.testUrl) {
            var d = t.getMessage();
            if (null != d && ("function" == typeof d.onDoneC && (e = d.onDoneC, delete d.onDoneC), "undefined" == typeof d.sent && c.sandbox && a.source == document.getElementById("keepa_data").contentWindow)) {
              if (c.sandbox == d.url) {
                t.setStatTime(40);
                try {
                  a.source.postMessage({key:"data", value:d}, "*");
                } catch (W) {
                  t.abortJob(407), e();
                }
              } else {
                c.isUrlMsg ? (d.wasUrl = c.sandbox, t.abortJob(405)) : (a = t.getOutgoingMessage(d, c.sandbox), p.sendMessage(a)), e();
              }
            }
          }
        }
      }
    });
    k ? c.set("addonVersionFirefox", l.version) : c.set("addonVersionChrome", l.version);
    try {
      chrome.runtime.setUninstallURL("https://dyn.keepa.com/app/stats/?type=uninstall&version=" + N + "." + l.version);
    } catch (e) {
    }
    window.setTimeout(function() {
      p.initWebSocket();
    }, 2000);
  }, log:function(a) {
    c.log(a);
  }, lastBugReport:0, reportBug:function(a, d, e) {
    var b = Error();
    c.get(["token"], function(c) {
      var h = Date.now();
      if (!(12E5 > h - l.lastBugReport || /(dead object)|(Script error)|(setUninstallURL)|(File error: Corrupted)|(operation is insecure)|(\.location is null)/i.test(a))) {
        l.lastBugReport = h;
        h = "";
        var g = l.version;
        d = d || "";
        try {
          if (h = b.stack.split("\n").splice(1).splice(1).join("&ensp;&lArr;&ensp;"), !/(keepa|content)\.js/.test(h) || h.startsWith("https://www.amazon") || h.startsWith("https://smile.amazon") || h.startsWith("https://sellercentral")) {
            return;
          }
        } catch (U) {
        }
        try {
          h = h.replace(/chrome-extension:\/\/.*?\/content\//g, "").replace(/:[0-9]*?\)/g, ")").replace(/[ ]{2,}/g, "");
        } catch (U) {
        }
        if ("object" == typeof a) {
          try {
            a = a instanceof Error ? a.toString() : JSON.stringify(a);
          } catch (U) {
          }
        }
        null == e && (e = {exception:a, additional:d, url:document.location.host, stack:h});
        e.keepaType = N;
        e.version = g;
        setTimeout(function() {
          l.httpPost("https://dyn.keepa.com/service/bugreport/?user=" + c.token + "&type=" + Z + "&version=" + g, JSON.stringify(e), null, !1);
        }, 50);
      }
    });
  }, httpGet:function(a, c, e, b) {
    var d = new XMLHttpRequest;
    c && (d.onreadystatechange = function() {
      4 == d.readyState && c.call(this, d.responseText, d.status);
    });
    d.withCredentials = e;
    d.open("GET", a, !0);
    b && d.setRequestHeader("krequestid", b);
    d.send();
  }, httpPost:function(a, c, e, b, g) {
    var d = new XMLHttpRequest;
    e && (d.onreadystatechange = function() {
      4 == d.readyState && e.call(this, d.responseText, d.status);
    });
    d.withCredentials = b;
    d.open("POST", a, !0);
    d.setRequestHeader("Content-Type", "text/plain;charset=UTF-8");
    g && d.setRequestHeader("krequestid", g);
    d.send(c);
  }};
  window.addEventListener("error", function(a, c, e, b, g) {
    a = "object" === typeof a && a.srcElement && a.target ? "[object HTMLScriptElement]" == a.srcElement && "[object HTMLScriptElement]" == a.target ? "Error loading script " + JSON.stringify(a) : JSON.stringify(a) : a.toString();
    var d = "";
    b = b || 0;
    if (g && g.stack) {
      d = g.stack;
      try {
        d = g.stack.split("\n").splice(1).splice(1).join("&ensp;&lArr;&ensp;");
        if (!/(keepa|content)\.js/.test(d)) {
          return;
        }
        d = d.replace(/chrome-extension:\/\/.*?\/content\//g, "").replace(/:[0-9]*?\)/g, ")").replace(/[ ]{2,}/g, "");
      } catch (W) {
      }
    }
    a = {msg:a, url:(c || document.location.toString()) + ":" + parseInt(e || 0) + ":" + parseInt(b || 0), stack:d};
    "ipbakfmnjdenbmoenhicfmoojdojjjem" != chrome.runtime.id && "blfpbjkajgamcehdbehfdioapoiibdmc" != chrome.runtime.id || console.log(a);
    l.reportBug(null, null, a);
    return !1;
  });
  var X = 0;
  var p = {server:["wss://dyn.keepa.com", "wss://dyn-2.keepa.com"], serverIndex:0, clearTimeout:0, webSocket:null, sendPlainMessage:function(a) {
    H || (a = JSON.stringify(a), p.webSocket.send(pako.deflate(a)));
  }, sendMessage:function(a) {
    if (!H) {
      t.clearIframe();
      var c = pako.deflate(JSON.stringify(a));
      t.clearMessage();
      1 == p.webSocket.readyState && p.webSocket.send(c);
      403 == a.status && t.endSession(X);
      g.console.clear();
    }
  }, initWebSocket:function() {
    H || c.get(["token", "optOut_crawl"], function(a) {
      var d = a.token, e = a.optOut_crawl;
      if (d && 64 == d.length) {
        var b = function() {
          if (null == p.webSocket || 1 != p.webSocket.readyState) {
            p.serverIndex %= p.server.length;
            if ("undefined" == typeof e || "undefined" == e || null == e || "null" == e || "NaN" == e) {
              e = "0";
            }
            q && (e = "1");
            "undefined" === typeof chrome.webRequest && (e = "1");
            var a = new WebSocket(p.server[p.serverIndex] + "/apps/cloud/?app=" + N + "&version=" + l.version + "&wr=" + typeof chrome.webRequest + "&optOut=" + e, d);
            a.binaryType = "arraybuffer";
            a.onmessage = function(a) {
              a = a.data;
              var b = null;
              a instanceof ArrayBuffer && (a = pako.inflate(a, {to:"string"}));
              try {
                b = JSON.parse(a);
              } catch (U) {
                l.reportBug(U, a);
                return;
              }
              108 == b.status ? 1 === b.guest ? (c.isGuest = !0, c.actionUrl = b.actionUrl) : c.isGuest = !1 : "" == b.key ? c.stockData.domainId = b.domainId : 108108 == b.timeout ? (b.stockData && (c.stockData = b.stockData, console.log("stock reveal ready")), "undefined" != typeof b.keepaBoxPlaceholder && c.set("keepaBoxPlaceholder", b.keepaBoxPlaceholder), "undefined" != typeof b.keepaBoxPlaceholderBackup && c.set("keepaBoxPlaceholderBackup", b.keepaBoxPlaceholderBackup), "undefined" != typeof b.keepaBoxPlaceholderBackupClass && 
              c.set("keepaBoxPlaceholderBackupClass", b.keepaBoxPlaceholderBackupClass), "undefined" != typeof b.keepaBoxPlaceholderAppend && c.set("keepaBoxPlaceholderAppend", b.keepaBoxPlaceholderAppend), "undefined" != typeof b.keepaBoxPlaceholderBackupAppend && c.set("keepaBoxPlaceholderBackupAppend", b.keepaBoxPlaceholderBackupAppend)) : (b.domainId && (X = b.domainId), t.clearIframe(), t.onMessage(b));
            };
            a.onclose = function(a) {
              setTimeout(function() {
                b();
              }, 36E4 * Math.random());
            };
            a.onerror = function(c) {
              p.serverIndex++;
              a.close();
            };
            a.onopen = function() {
              t.abortJob(414);
            };
            p.webSocket = a;
          }
        };
        b();
      }
    });
  }};
  var t = function() {
    function a(a) {
      try {
        n.stats.times.push(a), n.stats.times.push(Date.now() - n.stats.start);
      } catch (x) {
      }
    }
    function d(c, b) {
      c.sent = !0;
      a(25);
      var d = c.key, z = c.messageId;
      c = c.stats;
      try {
        var e = B[D]["session-id"];
      } catch (m) {
        e = "";
      }
      d = {key:d, messageId:z, stats:c, sessionId:e, payload:[], status:200};
      for (var x in b) {
        d[x] = b[x];
      }
      return d;
    }
    function e(c) {
      D = n.domainId;
      R = u(B);
      "object" != typeof B[D] && (B[D] = {});
      "undefined" == typeof n.headers.Accept && (n.headers.Accept = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*!/!*;q=0.8");
      f(c, !c.isAjax, function(b) {
        a(0);
        var z = {payload:[]};
        if (b.match(F)) {
          z.status = 403;
        } else {
          if (c.contentFilters && 0 < c.contentFilters.length) {
            for (var e in c.contentFilters) {
              var x = b.match(new RegExp(c.contentFilters[e]));
              if (x) {
                z.payload[e] = x[1].replace(/\n/g, "");
              } else {
                z.status = 305;
                z.payload[e] = b;
                break;
              }
            }
          } else {
            z.payload = [b];
          }
        }
        try {
          c.stats.times.push(3), c.stats.times.push(l.lastBugReport);
        } catch (r) {
        }
        "undefined" == typeof c.sent && (z = d(c, z), p.sendMessage(z));
      });
    }
    function b(b) {
      D = n.domainId;
      R = u(B);
      "object" != typeof B[D] && (B[D] = {});
      "undefined" == typeof n.headers.Accept && (n.headers.Accept = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*!/!*;q=0.8");
      a(4);
      var e = new URL(b.url), z = null;
      try {
        null != b.scrapeFilters && 0 < b.scrapeFilters.length && b.scrapeFilters[0].lager && chrome.cookies.get({url:e.origin, name:"session-id"}, function(a) {
          null == a ? z = "guest" : null != a.value && 5 < a.value.length && (z = a.value);
        });
      } catch (A) {
      }
      f(b, !b.isAjax, function(x, g) {
        a(6);
        if ("undefined" == typeof b.sent) {
          var h = {};
          try {
            for (var m = x.evaluate("//comment()", x, null, XPathResult.ANY_TYPE, null), f = m.iterateNext(), n = ""; f;) {
              n += f.textContent, f = m.iterateNext();
            }
            if (x.querySelector("body").textContent.match(F) || n.match(F)) {
              h.status = 403;
              if ("undefined" != typeof b.sent) {
                return;
              }
              h = d(b, h);
              p.sendMessage(h);
              return;
            }
          } catch (G) {
          }
          a(7);
          if (b.scrapeFilters && 0 < b.scrapeFilters.length) {
            var P = {}, A = {}, J = {}, k = "", t = null, u = function() {
              if ("" === k) {
                h.payload = [t];
                h.scrapedData = J;
                for (var a in A) {
                  h[a] = A[a];
                }
              } else {
                h.status = 305, h.payload = [t, k, ""];
              }
              try {
                b.stats.times.push(99), b.stats.times.push(l.lastBugReport);
              } catch (ba) {
              }
              "undefined" == typeof b.sent && (h = d(b, h), p.sendMessage(h));
            }, v = function(a, b, c) {
              var d = [];
              if (!a.selector) {
                if (!a.regExp) {
                  return k = "invalid selector, sel/regexp", !1;
                }
                d = x.querySelector("html").innerHTML.match(new RegExp(a.regExp));
                if (!d || d.length < a.reGroup) {
                  c = "regexp fail: html - " + a.name + c;
                  if (!1 === a.optional) {
                    return k = c, !1;
                  }
                  t += " // " + c;
                  return !0;
                }
                return d[a.reGroup];
              }
              var e = b.querySelectorAll(a.selector);
              0 == e.length && (e = b.querySelectorAll(a.altSelector));
              if (0 == e.length) {
                if (!0 === a.optional) {
                  return !0;
                }
                k = "selector no match: " + a.name + c;
                return !1;
              }
              if (a.parentSelector && (e = [e[0].parentNode.querySelector(a.parentSelector)], null == e[0])) {
                if (!0 === a.optional) {
                  return !0;
                }
                k = "parent selector no match: " + a.name + c;
                return !1;
              }
              if ("undefined" != typeof a.multiple && null != a.multiple && (!0 === a.multiple && 1 > e.length || !1 === a.multiple && 1 < e.length)) {
                c = "selector multiple mismatch: " + a.name + c + " found: " + e.length;
                if (!1 === a.optional) {
                  return k = c, !1;
                }
                t += " // " + c;
                return !0;
              }
              if (a.isListSelector) {
                return P[a.name] = e, !0;
              }
              if (!a.attribute) {
                return k = "selector attribute undefined?: " + a.name + c, !1;
              }
              for (var z in e) {
                if (e.hasOwnProperty(z)) {
                  b = e[z];
                  if (!b) {
                    break;
                  }
                  if (a.childNode) {
                    a.childNode = Number(a.childNode);
                    b = b.childNodes;
                    if (b.length < a.childNode) {
                      c = "childNodes fail: " + b.length + " - " + a.name + c;
                      if (!1 === a.optional) {
                        return k = c, !1;
                      }
                      t += " // " + c;
                      return !0;
                    }
                    b = b[a.childNode];
                  }
                  b = "text" == a.attribute ? b.textContent : "html" == a.attribute ? b.innerHTML : b.getAttribute(a.attribute);
                  if (!b || 0 == b.length || 0 == b.replace(/(\r\n|\n|\r)/gm, "").replace(/^\s+|\s+$/g, "").length) {
                    c = "selector attribute null: " + a.name + c;
                    if (!1 === a.optional) {
                      return k = c, !1;
                    }
                    t += " // " + c;
                    return !0;
                  }
                  if (a.regExp) {
                    var g = b.match(new RegExp(a.regExp));
                    if (!g || g.length < a.reGroup) {
                      c = "regexp fail: " + b + " - " + a.name + c;
                      if (!1 === a.optional) {
                        return k = c, !1;
                      }
                      t += " // " + c;
                      return !0;
                    }
                    d.push("undefined" == typeof g[a.reGroup] ? g[0] : g[a.reGroup]);
                  } else {
                    d.push(b);
                  }
                  if (!a.multiple) {
                    break;
                  }
                }
              }
              return a.multiple ? d : d[0];
            };
            f = !1;
            m = {};
            for (var B in b.scrapeFilters) {
              m.$jscomp$loop$prop$pageType$75 = B;
              a: {
                if (f) {
                  break;
                }
                m.$jscomp$loop$prop$pageFilter$72 = b.scrapeFilters[m.$jscomp$loop$prop$pageType$75];
                m.$jscomp$loop$prop$pageVersionTest$73 = m.$jscomp$loop$prop$pageFilter$72.pageVersionTest;
                n = x.querySelectorAll(m.$jscomp$loop$prop$pageVersionTest$73.selector);
                0 == n.length && (n = x.querySelectorAll(m.$jscomp$loop$prop$pageVersionTest$73.altSelector));
                if (0 != n.length) {
                  if ("undefined" != typeof m.$jscomp$loop$prop$pageVersionTest$73.multiple && null != m.$jscomp$loop$prop$pageVersionTest$73.multiple) {
                    if (!0 === m.$jscomp$loop$prop$pageVersionTest$73.multiple && 2 > n.length) {
                      break a;
                    }
                    if (!1 === m.$jscomp$loop$prop$pageVersionTest$73.multiple && 1 < n.length) {
                      break a;
                    }
                  }
                  if (m.$jscomp$loop$prop$pageVersionTest$73.attribute) {
                    var C = null;
                    C = "text" == m.$jscomp$loop$prop$pageVersionTest$73.attribute ? "" : n[0].getAttribute(m.$jscomp$loop$prop$pageVersionTest$73.attribute);
                    if (null == C) {
                      break a;
                    }
                  }
                  var y = m.$jscomp$loop$prop$pageType$75;
                  m.$jscomp$loop$prop$revealMAP$92 = m.$jscomp$loop$prop$pageFilter$72.revealMAP;
                  m.$jscomp$loop$prop$revealed$94 = !1;
                  m.$jscomp$loop$prop$afterAjaxFinished$95 = function(d) {
                    return function() {
                      var g = 0, m = [];
                      a(26);
                      var f = {}, l;
                      for (l in d.$jscomp$loop$prop$pageFilter$72) {
                        f.$jscomp$loop$prop$sel$81 = d.$jscomp$loop$prop$pageFilter$72[l];
                        if (!(f.$jscomp$loop$prop$sel$81.name == d.$jscomp$loop$prop$pageVersionTest$73.name || d.$jscomp$loop$prop$revealed$94 && "revealMAP" == f.$jscomp$loop$prop$sel$81.name)) {
                          var n = x;
                          if (f.$jscomp$loop$prop$sel$81.parentList) {
                            var k = [];
                            if ("undefined" != typeof P[f.$jscomp$loop$prop$sel$81.parentList]) {
                              k = P[f.$jscomp$loop$prop$sel$81.parentList];
                            } else {
                              if (!0 === v(d.$jscomp$loop$prop$pageFilter$72[f.$jscomp$loop$prop$sel$81.parentList], n, d.$jscomp$loop$prop$pageType$75)) {
                                k = P[f.$jscomp$loop$prop$sel$81.parentList];
                              } else {
                                break;
                              }
                            }
                            A[f.$jscomp$loop$prop$sel$81.parentList] || (A[f.$jscomp$loop$prop$sel$81.parentList] = []);
                            n = 0;
                            var r = {}, p;
                            for (p in k) {
                              if (k.hasOwnProperty(p)) {
                                if ("lager" == f.$jscomp$loop$prop$sel$81.name) {
                                  n++;
                                  try {
                                    var w = void 0;
                                    r.$jscomp$loop$prop$offerId$78 = void 0;
                                    f.$jscomp$loop$prop$sel$81.selector && (w = k[p].querySelector(f.$jscomp$loop$prop$sel$81.selector));
                                    f.$jscomp$loop$prop$sel$81.altSelector && (r.$jscomp$loop$prop$offerId$78 = k[p].querySelector(f.$jscomp$loop$prop$sel$81.altSelector));
                                    r.$jscomp$loop$prop$offerId$78 && (r.$jscomp$loop$prop$offerId$78 = r.$jscomp$loop$prop$offerId$78.getAttribute(f.$jscomp$loop$prop$sel$81.attribute));
                                    r.$jscomp$loop$prop$maxQty$79 = 999;
                                    if (!r.$jscomp$loop$prop$offerId$78) {
                                      try {
                                        var G = JSON.parse(f.$jscomp$loop$prop$sel$81.regExp);
                                        if (G.sel1) {
                                          try {
                                            var B = JSON.parse(k[p].querySelectorAll(G.sel1)[0].dataset[G.dataSet1]);
                                            r.$jscomp$loop$prop$offerId$78 = B[G.val1];
                                            r.$jscomp$loop$prop$maxQty$79 = B.maxQty;
                                          } catch (S) {
                                          }
                                        }
                                        if (!r.$jscomp$loop$prop$offerId$78 && G.sel2) {
                                          try {
                                            var C = JSON.parse(k[p].querySelectorAll(G.sel2)[0].dataset[G.dataSet2]);
                                            r.$jscomp$loop$prop$offerId$78 = C[G.val2];
                                            r.$jscomp$loop$prop$maxQty$79 = C.maxQty;
                                          } catch (S) {
                                          }
                                        }
                                      } catch (S) {
                                      }
                                    }
                                    if (w && r.$jscomp$loop$prop$offerId$78 && null != z) {
                                      g++;
                                      r.$jscomp$loop$prop$mapIndex$84 = p + "";
                                      r.$jscomp$loop$prop$isMAP$82 = !1;
                                      try {
                                        r.$jscomp$loop$prop$isMAP$82 = A[f.$jscomp$loop$prop$sel$81.parentList][r.$jscomp$loop$prop$mapIndex$84].isMAP || -1 != k[p].textContent.toLowerCase().indexOf("add to cart to see product details");
                                      } catch (S) {
                                      }
                                      r.$jscomp$loop$prop$busy$83 = !0;
                                      r.$jscomp$loop$prop$currentASIN$77 = b.url.match(/([BC][A-Z0-9]{9}|\d{9}(!?X|\d))/)[1];
                                      null == r.$jscomp$loop$prop$currentASIN$77 || 9 > r.$jscomp$loop$prop$currentASIN$77.length || setTimeout(function(a, d) {
                                        return function() {
                                          c.addStockJob({type:"getStock", asin:a.$jscomp$loop$prop$currentASIN$77, oid:a.$jscomp$loop$prop$offerId$78, host:e.host, maxQty:a.$jscomp$loop$prop$maxQty$79, onlyMaxQty:9 == d.$jscomp$loop$prop$sel$81.reGroup, isMAP:a.$jscomp$loop$prop$isMAP$82, referer:e.host + "/dp/" + a.$jscomp$loop$prop$currentASIN$77, domainId:b.domainId, force:!0, session:z}, function(c) {
                                            a.$jscomp$loop$prop$busy$83 && (a.$jscomp$loop$prop$busy$83 = !1, "undefined" != typeof c && (A[d.$jscomp$loop$prop$sel$81.parentList][a.$jscomp$loop$prop$mapIndex$84][d.$jscomp$loop$prop$sel$81.name] = c), 0 == --g && u(h));
                                          });
                                          setTimeout(function() {
                                            a.$jscomp$loop$prop$busy$83 && 0 == --g && (a.$jscomp$loop$prop$busy$83 = !1, console.log("timeout " + a.$jscomp$loop$prop$offerId$78), u(h));
                                          }, 3000 + 800 * g);
                                        };
                                      }(r, f), 1);
                                    }
                                  } catch (S) {
                                  }
                                } else {
                                  if ("revealMAP" == f.$jscomp$loop$prop$sel$81.name) {
                                    if (r.$jscomp$loop$prop$revealMAP$49$85 = f.$jscomp$loop$prop$sel$81, w = void 0, w = r.$jscomp$loop$prop$revealMAP$49$85.selector ? k[p].querySelector(r.$jscomp$loop$prop$revealMAP$49$85.selector) : k[p], null != w && w.textContent.match(new RegExp(r.$jscomp$loop$prop$revealMAP$49$85.regExp))) {
                                      w = b.url.match(/([BC][A-Z0-9]{9}|\d{9}(!?X|\d))/)[1];
                                      var y = d.$jscomp$loop$prop$pageFilter$72.sellerId;
                                      "undefined" == typeof y || null == y || null == w || 2 > w.length || (y = k[p].querySelector(f.$jscomp$loop$prop$sel$81.childNode).value, null == y || 20 > y + 0 || (w = r.$jscomp$loop$prop$revealMAP$49$85.altSelector.replace("OFFERID", y).replace("ASINID", w), g++, r.$jscomp$loop$prop$mapIndex$52$86 = p + "", q(w, "GET", null, 3000, function(a) {
                                        return function(c) {
                                          try {
                                            var b = d.$jscomp$loop$prop$pageFilter$72.price;
                                            if (b && b.regExp) {
                                              if (c.match(/no valid offer--/)) {
                                                A[a.$jscomp$loop$prop$revealMAP$49$85.parentList][a.$jscomp$loop$prop$mapIndex$52$86] || (A[a.$jscomp$loop$prop$revealMAP$49$85.parentList][a.$jscomp$loop$prop$mapIndex$52$86] = {}), A[a.$jscomp$loop$prop$revealMAP$49$85.parentList][a.$jscomp$loop$prop$mapIndex$52$86][a.$jscomp$loop$prop$revealMAP$49$85.name] = -1;
                                              } else {
                                                var e = c.match(new RegExp("price info--\x3e(?:.|\\n)*?" + b.regExp + "(?:.|\\n)*?\x3c!--")), x = c.match(/price info--\x3e(?:.|\n)*?(?:<span.*?size-small.*?">)([^]*?<\/span)(?:.|\n)*?\x3c!--/);
                                                if (!e || e.length < b.reGroup) {
                                                  t += " //  priceMAP regexp fail: " + (c + " - " + b.name + d.$jscomp$loop$prop$pageType$75);
                                                } else {
                                                  var f = e[b.reGroup];
                                                  A[a.$jscomp$loop$prop$revealMAP$49$85.parentList][a.$jscomp$loop$prop$mapIndex$52$86] || (A[a.$jscomp$loop$prop$revealMAP$49$85.parentList][a.$jscomp$loop$prop$mapIndex$52$86] = {});
                                                  A[a.$jscomp$loop$prop$revealMAP$49$85.parentList][a.$jscomp$loop$prop$mapIndex$52$86][a.$jscomp$loop$prop$revealMAP$49$85.name] = f;
                                                  null != x && 2 == x.length && (A[a.$jscomp$loop$prop$revealMAP$49$85.parentList][a.$jscomp$loop$prop$mapIndex$52$86][a.$jscomp$loop$prop$revealMAP$49$85.name + "Shipping"] = x[1].replace(/(\r\n|\n|\r)/gm, " ").replace(/^\s+|\s+$/g, "").replace(/\s{2,}/g, " "));
                                                }
                                              }
                                            }
                                          } catch (ca) {
                                          }
                                          0 == --g && 0 == m.length && u();
                                        };
                                      }(r), function() {
                                        0 == --g && 0 == m.length && u();
                                      })));
                                    }
                                  } else {
                                    w = v(f.$jscomp$loop$prop$sel$81, k[p], d.$jscomp$loop$prop$pageType$75);
                                    if (!1 === w) {
                                      break;
                                    }
                                    if (!0 !== w) {
                                      if (A[f.$jscomp$loop$prop$sel$81.parentList][p] || (A[f.$jscomp$loop$prop$sel$81.parentList][p] = {}), f.$jscomp$loop$prop$sel$81.multiple) {
                                        for (var D in w) {
                                          w.hasOwnProperty(D) && !f.$jscomp$loop$prop$sel$81.keepBR && (w[D] = w[D].replace(/(\r\n|\n|\r)/gm, " ").replace(/^\s+|\s+$/g, "").replace(/\s{2,}/g, " "));
                                        }
                                        w = w.join("\u271c\u271c");
                                        A[f.$jscomp$loop$prop$sel$81.parentList][p][f.$jscomp$loop$prop$sel$81.name] = w;
                                      } else {
                                        A[f.$jscomp$loop$prop$sel$81.parentList][p][f.$jscomp$loop$prop$sel$81.name] = f.$jscomp$loop$prop$sel$81.keepBR ? w : w.replace(/(\r\n|\n|\r)/gm, " ").replace(/^\s+|\s+$/g, "").replace(/\s{2,}/g, " ");
                                      }
                                    }
                                  }
                                }
                              }
                              r = {$jscomp$loop$prop$currentASIN$77:r.$jscomp$loop$prop$currentASIN$77, $jscomp$loop$prop$offerId$78:r.$jscomp$loop$prop$offerId$78, $jscomp$loop$prop$maxQty$79:r.$jscomp$loop$prop$maxQty$79, $jscomp$loop$prop$isMAP$82:r.$jscomp$loop$prop$isMAP$82, $jscomp$loop$prop$busy$83:r.$jscomp$loop$prop$busy$83, $jscomp$loop$prop$mapIndex$84:r.$jscomp$loop$prop$mapIndex$84, $jscomp$loop$prop$revealMAP$49$85:r.$jscomp$loop$prop$revealMAP$49$85, $jscomp$loop$prop$mapIndex$52$86:r.$jscomp$loop$prop$mapIndex$52$86};
                            }
                          } else {
                            k = v(f.$jscomp$loop$prop$sel$81, n, d.$jscomp$loop$prop$pageType$75);
                            if (!1 === k) {
                              break;
                            }
                            if (!0 !== k) {
                              if (f.$jscomp$loop$prop$sel$81.multiple) {
                                for (var E in k) {
                                  k.hasOwnProperty(E) && !f.$jscomp$loop$prop$sel$81.keepBR && (k[E] = k[E].replace(/(\r\n|\n|\r)/gm, " ").replace(/^\s+|\s+$/g, "").replace(/\s{2,}/g, " "));
                                }
                                k = k.join();
                              } else {
                                f.$jscomp$loop$prop$sel$81.keepBR || (k = k.replace(/(\r\n|\n|\r)/gm, " ").replace(/^\s+|\s+$/g, "").replace(/\s{2,}/g, " "));
                              }
                              J[f.$jscomp$loop$prop$sel$81.name] = k;
                            }
                          }
                        }
                        f = {$jscomp$loop$prop$sel$81:f.$jscomp$loop$prop$sel$81};
                      }
                      try {
                        if (1 == m.length || "500".endsWith("8") && 0 < m.length) {
                          m.shift()();
                        } else {
                          for (f = 0; f < m.length; f++) {
                            setTimeout(function() {
                              0 < m.length && m.shift()();
                            }, 500 * f);
                          }
                        }
                      } catch (S) {
                      }
                      0 == g && 0 == m.length && u();
                    };
                  }(m);
                  if (m.$jscomp$loop$prop$revealMAP$92) {
                    if (f = x.querySelector(m.$jscomp$loop$prop$revealMAP$92.selector), null != f) {
                      m.$jscomp$loop$prop$url$93 = f.getAttribute(m.$jscomp$loop$prop$revealMAP$92.attribute);
                      if (null == m.$jscomp$loop$prop$url$93 || 0 == m.$jscomp$loop$prop$url$93.length) {
                        m.$jscomp$loop$prop$afterAjaxFinished$95();
                        break;
                      }
                      0 != m.$jscomp$loop$prop$url$93.indexOf("http") && (f = document.createElement("a"), f.href = b.url, m.$jscomp$loop$prop$url$93 = f.origin + m.$jscomp$loop$prop$url$93);
                      J[m.$jscomp$loop$prop$revealMAP$92.name] = "1";
                      m.$jscomp$loop$prop$url$93 = m.$jscomp$loop$prop$url$93.replace(/(mapPopover.*?)(false)/, "$1true");
                      m.$jscomp$loop$prop$xhr$90 = new XMLHttpRequest;
                      m.$jscomp$loop$prop$hasTimeout$89 = !1;
                      m.$jscomp$loop$prop$ti$91 = setTimeout(function(a) {
                        return function() {
                          a.$jscomp$loop$prop$hasTimeout$89 = !0;
                          a.$jscomp$loop$prop$afterAjaxFinished$95();
                        };
                      }(m), 4000);
                      m.$jscomp$loop$prop$xhr$90.onreadystatechange = function(a) {
                        return function() {
                          if (!a.$jscomp$loop$prop$hasTimeout$89 && 4 == a.$jscomp$loop$prop$xhr$90.readyState) {
                            clearTimeout(a.$jscomp$loop$prop$ti$91);
                            if (200 == a.$jscomp$loop$prop$xhr$90.status) {
                              var c = a.$jscomp$loop$prop$xhr$90.responseText;
                              if (a.$jscomp$loop$prop$revealMAP$92.regExp) {
                                var b = c.match(new RegExp(a.$jscomp$loop$prop$revealMAP$92.regExp));
                                if (!b || b.length < a.$jscomp$loop$prop$revealMAP$92.reGroup) {
                                  if (b = x.querySelector(a.$jscomp$loop$prop$revealMAP$92.selector)) {
                                    var d = b.cloneNode(!1);
                                    d.innerHTML = c;
                                    b.parentNode.replaceChild(d, b);
                                  }
                                } else {
                                  J[a.$jscomp$loop$prop$revealMAP$92.name] = b[a.$jscomp$loop$prop$revealMAP$92.reGroup], J[a.$jscomp$loop$prop$revealMAP$92.name + "url"] = a.$jscomp$loop$prop$url$93;
                                }
                              }
                            }
                            a.$jscomp$loop$prop$revealed$94 = !0;
                            a.$jscomp$loop$prop$afterAjaxFinished$95();
                          }
                        };
                      }(m);
                      m.$jscomp$loop$prop$xhr$90.onerror = m.$jscomp$loop$prop$afterAjaxFinished$95;
                      m.$jscomp$loop$prop$xhr$90.open("GET", m.$jscomp$loop$prop$url$93, !0);
                      m.$jscomp$loop$prop$xhr$90.send();
                    } else {
                      m.$jscomp$loop$prop$afterAjaxFinished$95();
                    }
                  } else {
                    m.$jscomp$loop$prop$afterAjaxFinished$95();
                  }
                  f = !0;
                }
              }
              m = {$jscomp$loop$prop$pageFilter$72:m.$jscomp$loop$prop$pageFilter$72, $jscomp$loop$prop$pageVersionTest$73:m.$jscomp$loop$prop$pageVersionTest$73, $jscomp$loop$prop$revealed$94:m.$jscomp$loop$prop$revealed$94, $jscomp$loop$prop$pageType$75:m.$jscomp$loop$prop$pageType$75, $jscomp$loop$prop$hasTimeout$89:m.$jscomp$loop$prop$hasTimeout$89, $jscomp$loop$prop$afterAjaxFinished$95:m.$jscomp$loop$prop$afterAjaxFinished$95, $jscomp$loop$prop$xhr$90:m.$jscomp$loop$prop$xhr$90, $jscomp$loop$prop$ti$91:m.$jscomp$loop$prop$ti$91, 
              $jscomp$loop$prop$revealMAP$92:m.$jscomp$loop$prop$revealMAP$92, $jscomp$loop$prop$url$93:m.$jscomp$loop$prop$url$93};
            }
            a(8);
            if (null == y) {
              k += " // no pageVersion matched";
              h.payload = [t, k, b.dbg1 ? g : ""];
              h.status = 308;
              a(10);
              try {
                b.stats.times.push(99), b.stats.times.push(l.lastBugReport);
              } catch (G) {
              }
              "undefined" == typeof b.sent && (h = d(b, h), p.sendMessage(h));
            }
          } else {
            a(9), h.status = 306, "undefined" == typeof b.sent && (h = d(b, h), p.sendMessage(h));
          }
        }
      });
    }
    function f(b, c, d) {
      null == L || K || O();
      I = b;
      var e = b.messageId;
      setTimeout(function() {
        null != I && I.messageId == e && (I = I = null);
      }, b.timeout);
      b.onDoneC = function() {
        I = null;
      };
      if (c) {
        a(11), c = document.getElementById("keepa_data"), c.removeAttribute("srcdoc"), c.src = b.url;
      } else {
        var f = function(c) {
          a(12);
          if ("o0" == b.key) {
            d(c);
          } else {
            var e = document.getElementById("keepa_data_2");
            e.src = "";
            c = c.replace(/src=".*?"/g, 'src=""');
            if (null != b) {
              b.block && (c = c.replace(new RegExp(b.block, "g"), ""));
              a(13);
              var f = !1;
              e.srcdoc = c;
              a(18);
              e.onload = function() {
                a(19);
                f || (e.onload = void 0, f = !0, a(20), setTimeout(function() {
                  a(21);
                  var b = document.getElementById("keepa_data_2").contentWindow;
                  try {
                    d(b.document, c);
                  } catch (Y) {
                    l.reportBug(Y), y(410);
                  }
                }, 80));
              };
            }
            g.console.clear();
          }
        };
        c = 0;
        1 == b.httpMethod && (b.scrapeFilters && 0 < b.scrapeFilters.length && (E = b), N || (N = !0, b.l && 0 < b.l.length && (L = b.l, O(), c = 25)));
        setTimeout(function() {
          q(b.url, Q[b.httpMethod], b.postData, b.timeout, f);
        }, c);
      }
    }
    function h() {
      try {
        var a = document.getElementById("keepa_data");
        a.src = "";
        a.removeAttribute("srcdoc");
      } catch (P) {
      }
      try {
        var b = document.getElementById("keepa_data_2");
        b.src = "";
        b.removeAttribute("srcdoc");
      } catch (P) {
      }
      I = null;
    }
    function q(b, c, d, e, f) {
      var g = new XMLHttpRequest;
      if (f) {
        var x = !1, h = setTimeout(function() {
          x = !0;
          t.abortJob(413);
        }, e || 15000);
        g.onreadystatechange = function() {
          x || (2 == g.readyState && a(27), 4 == g.readyState && (clearTimeout(h), a(29), 503 != g.status && (0 == g.status || 399 < g.status) ? t.abortJob(415, [g.status]) : 0 == g.responseText.length && c == Q[0] ? t.abortJob(416) : f.call(this, g.responseText)));
        };
        g.onerror = function() {
          t.abortJob(408);
        };
      }
      g.open(c, b, !0);
      null == d ? g.send() : g.send(d);
    }
    function u(a) {
      var b = "", c = "", d;
      for (d in a[D]) {
        var e = a[D][d];
        "-" != e && (b += c + d + "=" + e + ";", c = " ");
      }
      return b;
    }
    function C(a) {
      delete B["" + a];
      localStorage.cache = pako.deflate(JSON.stringify(B), {to:"string"});
    }
    function y(a, b) {
      if (null != n) {
        try {
          if ("undefined" != typeof n.sent) {
            return;
          }
          var c = d(n, {});
          b && (c.payload = b);
          c.status = a;
          p.sendMessage(c);
          h();
        } catch (A) {
          l.reportBug(A, "abort");
        }
      }
      g.console.clear();
    }
    var E = null, n = null, F = /automated access|api-services-support@/, H = [function(a) {
    }, function(a) {
      if (null != n) {
        var b = !0;
        if (a.initiator) {
          if (a.initiator.startsWith("http")) {
            return;
          }
        } else {
          if (a.originUrl && !a.originUrl.startsWith("moz-extension")) {
            return;
          }
        }
        if (n.url == a.url) {
          M = a.frameId, T = a.tabId, V = a.parentFrameId, b = !1;
        } else {
          if (M == a.parentFrameId || V == a.parentFrameId || M == a.frameId) {
            b = !1;
          }
        }
        if (-2 != M && !(0 < a.tabId && T != a.tabId)) {
          a = a.requestHeaders;
          var c = {};
          if (!a.find(function(a) {
            return "krequestid" === a.name;
          })) {
            "" === n.headers.Cookie && (b = !0);
            (n.timeout + "").endsWith("108") || (n.headers.Cookie = b ? "" : R);
            for (var d in n.headers) {
              b = !1;
              for (var e = 0; e < a.length; ++e) {
                if (a[e].name.toLowerCase() == d.toLowerCase()) {
                  "" == n.headers[d] ? (a.splice(e, 1), e--) : a[e].value = n.headers[d];
                  b = !0;
                  break;
                }
              }
              b || "" == n.headers[d] || a.push({name:k ? d.toLowerCase() : d, value:n.headers[d]});
            }
            c.requestHeaders = a;
            return c;
          }
        }
      }
    }, function(a) {
      var b = a.responseHeaders;
      try {
        if (a.initiator) {
          if (a.initiator.startsWith("http")) {
            return;
          }
        } else {
          if (a.originUrl && !a.originUrl.startsWith("moz-extension")) {
            return;
          }
        }
        if (0 < a.tabId && T != a.tabId || null == n || b.find(function(a) {
          return "krequestid" === a.name;
        })) {
          return;
        }
        for (var d = (n.timeout + "").endsWith("108"), e = !1, g = [], f = 0; f < b.length; f++) {
          var h = b[f], l = h.name.toLowerCase();
          "set-cookie" == l ? (-1 < h.value.indexOf("xpires") && c.parseCookieHeader(g, h.value), d || b.splice(f--, 1)) : "x-frame-options" == l && (b.splice(f, 1), f--);
        }
        for (f = 0; f < g.length; f++) {
          var k = g[f];
          if ("undefined" == typeof B[D][k[0]] || B[D][k[0]] != k[1]) {
            e = !0, B[D][k[0]] = k[1];
          }
        }
        !d && e && n.url == a.url && (localStorage.cache = pako.deflate(JSON.stringify(B), {to:"string"}), R = u(B));
      } catch (Y) {
      }
      return {responseHeaders:b};
    }, function(a) {
      if (null != n && n.url == a.url) {
        var b = 0;
        switch(a.error) {
          case "net::ERR_TUNNEL_CONNECTION_FAILED":
            b = 510;
            break;
          case "net::ERR_INSECURE_RESPONSE":
            b = 511;
            break;
          case "net::ERR_CONNECTION_REFUSED":
            b = 512;
            break;
          case "net::ERR_BAD_SSL_CLIENT_AUTH_CERT":
            b = 513;
            break;
          case "net::ERR_CONNECTION_CLOSED":
            b = 514;
            break;
          case "net::ERR_NAME_NOT_RESOLVED":
            b = 515;
            break;
          case "net::ERR_NAME_RESOLUTION_FAILED":
            b = 516;
            break;
          case "net::ERR_ABORTED":
          case "net::ERR_CONNECTION_ABORTED":
            b = 517;
            break;
          case "net::ERR_CONTENT_DECODING_FAILED":
            b = 518;
            break;
          case "net::ERR_NETWORK_ACCESS_DENIED":
            b = 519;
            break;
          case "net::ERR_NETWORK_CHANGED":
            b = 520;
            break;
          case "net::ERR_INCOMPLETE_CHUNKED_ENCODING":
            b = 521;
            break;
          case "net::ERR_CONNECTION_TIMED_OUT":
          case "net::ERR_TIMED_OUT":
            b = 522;
            break;
          case "net::ERR_CONNECTION_RESET":
            b = 523;
            break;
          case "net::ERR_NETWORK_IO_SUSPENDED":
            b = 524;
            break;
          case "net::ERR_EMPTY_RESPONSE":
            b = 525;
            break;
          case "net::ERR_SSL_PROTOCOL_ERROR":
            b = 526;
            break;
          case "net::ERR_ADDRESS_UNREACHABLE":
            b = 527;
            break;
          case "net::ERR_INTERNET_DISCONNECTED":
            b = 528;
            break;
          case "net::ERR_BLOCKED_BY_ADMINISTRATOR":
            b = 529;
            break;
          case "net::ERR_SSL_VERSION_OR_CIPHER_MISMATCH":
            b = 530;
            break;
          case "net::ERR_CONTENT_LENGTH_MISMATCH":
            b = 531;
            break;
          case "net::ERR_PROXY_CONNECTION_FAILED":
            b = 532;
            break;
          default:
            b = 533;
            return;
        }
        setTimeout(function() {
          t.setStatTime(33);
          t.abortJob(b);
        }, 0);
      }
    }], N = !1, K = !1, L = null, I = null, O = function() {
      K = !0;
      for (var a = 0; a < L.length; a++) {
        var b = L[a], c = window, d = 0;
        try {
          for (; d < b.path.length - 1; d++) {
            c = c[b.path[d]];
          }
          delete b.a.types;
          if (b.b) {
            c[b.path[d]](H[b.index], b.a, b.b);
          } else {
            c[b.path[d]](H[b.index], b.a);
          }
        } catch (J) {
          console.log(J);
        }
      }
      g.console.clear();
    }, Q = ["GET", "HEAD", "POST", "PUT", "DELETE"], B = {}, R = "", D = 1;
    try {
      localStorage.cache && (B = JSON.parse(pako.inflate(localStorage.cache, {to:"string"})));
    } catch (z) {
      setTimeout(function() {
        l.reportBug(z, pako.inflate(localStorage.cache, {to:"string"}));
      }, 2000);
    }
    var M = -2, T = -1, V = -2;
    return {onMessage:function(a) {
      "hhhh" == a.key && chrome.webRequest.onBeforeSendHeaders.addListener(function(a) {
        if (null != n) {
          var b = !0;
          if (a.initiator) {
            if (a.initiator.startsWith("http")) {
              return;
            }
          } else {
            if (a.originUrl && !a.originUrl.startsWith("moz-extension")) {
              return;
            }
          }
          n.url == a.url && (M = a.frameId, T = a.tabId, V = a.parentFrameId, b = !1);
          if (-2 != M && M == a.frameId && T == a.tabId && V == a.parentFrameId) {
            a = a.requestHeaders;
            var c = {};
            (n.timeout + "").endsWith("108") || (n.headers.Cookie = b ? "" : R);
            for (var d in n.headers) {
              b = !1;
              for (var e = 0; e < a.length; ++e) {
                if (a[e].name.toLowerCase() == d.toLowerCase()) {
                  "" == n.headers[d] ? a.splice(e, 1) : a[e].value = n.headers[d];
                  b = !0;
                  break;
                }
              }
              b || "" == n.headers[d] || a.push({name:k ? d.toLowerCase() : d, value:n.headers[d]});
            }
            c.requestHeaders = a;
            return c;
          }
        }
      }, {urls:["<all_urls>"]}, ["blocking", "requestHeaders"]);
      switch(a.key) {
        case "o0":
        case "o1":
          n = a, n.stats = {start:Date.now(), times:[]};
      }
      switch(a.key) {
        case "update":
          chrome.runtime.requestUpdateCheck(function(a, b) {
            console.log(a, b);
            "update_available" == a && chrome.runtime.reload();
          });
          break;
        case "o0":
          t.clearIframe();
          e(a);
          break;
        case "o1":
          t.clearIframe();
          b(a);
          break;
        case "o2":
          C(a.domainId);
          break;
        case "1":
          document.location.reload(!1);
      }
    }, clearIframe:h, endSession:C, getOutgoingMessage:d, setStatTime:a, getFilters:function() {
      return E;
    }, getMessage:function() {
      return n;
    }, clearMessage:function() {
      n = null;
      if (null != L && K) {
        K = !1;
        for (var a = 0; a < L.length; a++) {
          var b = L[a];
          if (b) {
            try {
              for (var c = window, d = 0; d < b.path.length - 1; d++) {
                c = c[b.path[d]];
              }
              c.removeListener(H[b.index]);
            } catch (J) {
            }
          }
        }
        g.console.clear();
      }
    }, abortJob:y};
  }();
})();

