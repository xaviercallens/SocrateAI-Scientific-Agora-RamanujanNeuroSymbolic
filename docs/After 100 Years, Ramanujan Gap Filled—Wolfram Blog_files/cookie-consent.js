        (function(){
            if (document.readyState === "loading") {
                document.addEventListener("DOMContentLoaded", run);
            } else {
                run();
            }

            function run(){

                if(shouldRender()){
                    let parent = '';
                    let wrapper = document.createElement('div');
                    wrapper.id = '__cookie-consent-wrapper';

                    if (parent !== '' && document.getElementById(parent) !== null) {
                        document.getElementById(parent).appendChild(wrapper);
                    }else{
                        document.body.appendChild(wrapper);
                    }

                    wrapper.innerHTML = '<div id=__cookie-consent-styles style=display:none><style>#__cookie-consent,#__cookie-consent *{color:#fff;font-family:Arial,sans-serif;font-weight:400;line-height:1.2;margin:0;padding:0;z-index:3000000000}@keyframes slideup{0%{bottom:-70px}100%{bottom:0}}#__cookie-consent{animation-name:slideup;animation-delay:1s;animation-duration:.5s;animation-fill-mode:forwards;animation-iteration-count:1;animation-timing-function:ease;background:rgba(101,101,101,.9);bottom:-70px;height:70px;left:0;min-width:320px;position:fixed;right:0;width:100%}#__cookie-consent-table{display:table;width:100%}#__cookie-consent-left,#__cookie-consent-right{display:table-cell;font-size:13px;height:70px;vertical-align:middle}#__cookie-consent-left{line-height:1.2;padding:0 15px;text-align:left}#__cookie-consent-right{padding:0 15px 0 0;text-align:right}#__cookie-consent-button{background:#51a9b1;border-radius:4px;border:1px solid #6c6c6c;cursor:pointer;padding:5px 15px;white-space:nowrap}#__cookie-consent-button:hover{background:#55b8c0}#__cookie-consent-link{color:#bdf4f8;text-decoration:none}#__cookie-consent-link:hover{border-bottom:1px dashed #bdf4f8;color:#bdf4f8}@media all and (max-width:600px){#__cookie-consent-left{font-size:10px}#__cookie-consent-button{font-size:12px}#__cookie-consent-button span:before{clear:both;content:\'\';display:table}}</style></div><div id=__cookie-consent><div id=__cookie-consent-table><div id=__cookie-consent-left>Ce site internet utilise des cookies pour optimiser votre experience de nos services sur le site selon les conditions prévues par notre <a href=http://www.wolfram.com/legal/privacy/wolfram-research.html target=_blank id=__cookie-consent-link>politique de confidentialité</a>.</div><div id=__cookie-consent-right><button id=__cookie-consent-button type=button>Accepter <span>et Fermer</span></span></button></div></div></div>';

                    document.getElementById('__cookie-consent-button').addEventListener('click', closeClicked, false);
                }

                function closeClicked(e){
                    wrapper = document.getElementById('__cookie-consent-wrapper');
                    if (wrapper !== null) {
                        wrapper.style.display = 'none';
                        wrapper.outerHTML = '';
                    }

                    setCookie();
                }

                function shouldRender(){
                    let cookies = {};
                    let rawCookies = document.cookie.split(';');
                    for (let i = 0; i < rawCookies.length; i++) {
                        let bits = rawCookies[i].split('=');
                        cookies[bits[0].trim()] = bits[1].trim();
                    }

                    if(cookies.hasOwnProperty('__cookie_consent')){
                        let cookieValue = cookies['__cookie_consent'];
                        if(cookieValue == 0){
                            return true;
                        }else{
                            return false;
                        }
                    }else{
                        return true;
                    }
                }

                function setCookie(){
                    let domain = '.wolfram.com';
                    let expire = new Date();
                    expire.setSeconds(expire.getSeconds() + 31536000);
                    document.cookie = '__cookie_consent=1;' + 'expires=' + expire + ';domain=' + domain + ';path=/';
                }
            }
        })(window);
