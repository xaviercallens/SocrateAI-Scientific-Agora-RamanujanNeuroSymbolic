// 
// If you need to add the notification to a WordPress site (e.g. support.wolfram.com), you'll need to update that server.
//

document.addEventListener("DOMContentLoaded", function(event) { 

    function stringMatchQ(str, rule) {
        var escapeRegex = (str) => str.replace(/([.*+?^=!:${}()|\[\]\/\\])/g, "\\$1");
        return new RegExp("^" + rule.split("*").map(escapeRegex).join(".*") + "$").test(str);
    }


// Make your own css here, if needed 
    function defaultCSS() {
        return `
<style>
#notice {
    background: #4f4f4f;
}
#notice-content {
    align-items: start;
    color: #fff; 
    display: grid;
    font-family: 'Source Sans Pro', sans-serif; 
    font-size: 15px;
    gap: 30px;
    grid-template-columns: 49px 1fr;
    line-height: 20px;
    margin: 0 auto;
    max-width: 1100px;
    padding: 2rem;
}
#notice-content svg {
    margin-top: 4px;
}
#notice-content div:first-child {
    color: #3ed4ff;
    font-size: 18px;
    padding-bottom: 0.5rem;
    text-transform: uppercase;
}
#notice-content a { 
  color:#a3e0f1;
  text-decoration: none; 
}
#notice-content a:hover { 
    color: #3ed4ff; 
}
</style>`;
    }


// Make your own css here, if needed 
    function customCSS() {
        if(stringMatchQ(window.location.hostname, 'www*.wolfram.com') && stringMatchQ(window.location.pathname, '/hackathons/')) {
            var bannerbg = "#df4905";
            var bannerhover = "#db1a10";
        } else if(stringMatchQ(window.location.hostname, 'www*.wolfram.com') && stringMatchQ(window.location.pathname, '/llm-researchers-ai-tools/')){
            var bannerbg = "#021823";
            var bannerhover = "#01131c";
        } else if(stringMatchQ(window.location.hostname, 'www*.wolfram.com') && stringMatchQ(window.location.pathname, '/wolfram-one/')){
            var bannerbg = "#13909b";
            var bannerhover = "#1eabb7";
        } else {
            var bannerbg = "#f86300";
            var bannerhover = "#f88900";
        }
        return `
<style>
#announce-stripe {
    background: ${bannerbg};
    box-sizing: border-box;
    color: #fff;
    font-family: 'Source Sans Pro', Arial, sans-serif;
    font-size: 18px;
    font-weight: 400;
    line-height: 1;
    width: 100%;
}
#announce-stripe:hover { background: ${bannerhover}; }
#announce-stripe a {
    align-items: center;
    color: #fff;
    display: grid;
    grid-template-columns: max-content;
    justify-items: center;
    justify-content: center;
    padding: 20px 60px 18px;
    text-decoration: none;
}
#announce-stripe a span::before {
    content: '';
    background:  url('/common/images/icon-notebook-assistant.png') no-repeat;
    background-size: 30px auto;
    width: 30px;
    height: 30px;
    display: inline-block;
    vertical-align: middle;
    position: relative;
    top: -1px;
    margin-right: 5px;
}
#announce-stripe a span::after {
    content: '\\00BB';
    display: inline;
    margin-left: 2px;
}
/*mathematica padding*/
#_product-header + style + #announce-stripe a { padding: 6px 60px 4px; }


@media (max-width: 600px) {
    #announce-stripe { font-size: 16px; }
    #announce-stripe a { 
       grid-template-columns: 1fr; 
        padding: 10px 20px; 
    }
    #announce-stripe a span::before { display: none; }

    /*mathematica padding*/
    #_product-header + style + #announce-stripe a { padding: 6px 20px; }
}
</style>`;
    }





// Put your messages here
    function message1(css) {
        return `<!-- Notice Stripe -->
                ${css}
                <div id="notice">
                    <div id="notice-content">
                        <svg id="Error" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 49 44" width="49" height="44"> <path d="M48.29,37.55L27.69,1.9c-1.46-2.54-5.12-2.54-6.59,0L.52,37.55c-1.47,2.54,.36,5.71,3.29,5.71H44.98c2.93,0,4.77-3.17,3.3-5.71ZM27.24,12.87l-.79,16.3h-4.1l-.83-16.3h5.73Zm-2.85,24.65c-1.94,0-3.24-1.4-3.24-3.27s1.33-3.27,3.24-3.27,3.17,1.37,3.2,3.27c0,1.87-1.26,3.27-3.2,3.27Z" fill="#3ed4ff"></path></svg>
                        <div>
                            <div>
                                <strong>OUTAGE NOTIFICATION::</strong>
                            </div>
                            <div>
                                Some Wolfram Language users are currently unable to access CloudConnect and related services (including AI Access and Wolfram Compute Services). We're actively investigating the issue and working to restore full functionality. If you need assistance while we work to resolve the issue, please <a href="https://www.wolfram.com/support/contact/">contact us</a>.
                            </div>
                        </div>
                    </div>
                </div>
                <!-- End Notice Stripe -->`;
    }

    function message2(css) {
        return `<!-- Notice Stripe -->
                ${css}
                <div id="notice">
                    <div id="notice-content">
                        <svg id="Error" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 49 44" width="49" height="44"> <path d="M48.29,37.55L27.69,1.9c-1.46-2.54-5.12-2.54-6.59,0L.52,37.55c-1.47,2.54,.36,5.71,3.29,5.71H44.98c2.93,0,4.77-3.17,3.3-5.71ZM27.24,12.87l-.79,16.3h-4.1l-.83-16.3h5.73Zm-2.85,24.65c-1.94,0-3.24-1.4-3.24-3.27s1.33-3.27,3.24-3.27,3.17,1.37,3.2,3.27c0,1.87-1.26,3.27-3.2,3.27Z" fill="#3ed4ff"></path></svg>
                        <div>
                            <div>
                                <strong>Maintenance Notification:</strong>
                            </div>
                            <div>
                                This form is temporarily unavailable due to scheduled maintenance. We anticipate completion by 8pm US Central Time (GMT-5) on Friday, October 3, 2025. Please try again later.
                            </div>
                        </div>
                    </div>
                </div>
                <!-- End Notice Stripe -->`;
    }

    function message3(css) {
        return `<!-- Notebook Assistant + LLM Kit Stripe -->
                ${css}
                <div id="announce-stripe">
                    <a href="/notebook-assistant-llm-kit/">
                        <span>Now Available: Wolfram Notebook Assistant + LLM&nbsp;Kit</span>
                    </a>
                </div>
                <!-- End Notebook Assistant + LLM Kit Stripe -->`;
    }


// Find where you want to insert the message based on a html's ID
//<!-- beforebegin -->
//<p>
//    <!-- afterbegin -->
//    foo
//    <!-- beforeend -->
//</p>
//<!-- afterend -->


/***********************************************/
/* Super Duper Alert Everywhere on wolfram.com */
/***********************************************/

//    if(stringMatchQ(window.location.hostname, 'www*.wolfram.com') && stringMatchQ(window.location.pathname, '/*')){
//         document.getElementById('_header').insertAdjacentHTML("afterend", message2(defaultCSS()));
//     }

/***********************************************/
/* Level 1 Alerts                              */
/***********************************************/

//    if(stringMatchQ(window.location.hostname, 'support*.wolfram.com') && stringMatchQ(window.location.pathname, '/*')){
//        document.getElementById('_header').insertAdjacentHTML("afterend", message1(defaultCSS()));
//    }

//    if(stringMatchQ(window.location.hostname, 'www*.wolfram.com') && stringMatchQ(window.location.pathname, '/support/contact/*')){
//        document.getElementById('_header').insertAdjacentHTML("afterend", message1(defaultCSS()));
//    }

//    if(stringMatchQ(window.location.hostname, 'www*.wolfram.com') && stringMatchQ(window.location.pathname, '/company/contact/')){
//        document.getElementById('_header').insertAdjacentHTML("afterend", message1(defaultCSS()));
//    }

//    if(stringMatchQ(window.location.hostname, 'www*.wolfram.com') && stringMatchQ(window.location.pathname, '/contact-us/')){
//        document.getElementById('_header').insertAdjacentHTML("afterend", message1(defaultCSS()));
//    }

/***********************************************/
/* Level 2 Alerts                              */
/***********************************************/

//    if(stringMatchQ(window.location.hostname, 'store*.wolfram.com') && stringMatchQ(window.location.pathname, '/*')){
//        document.getElementById('gl-header').insertAdjacentHTML("afterend", message1(defaultCSS()));
//    }

//    if(stringMatchQ(window.location.hostname, 'www*.wolfram.com') && stringMatchQ(window.location.pathname, '/siteinfo/')){
//        document.getElementById('_header').insertAdjacentHTML("afterend", message1(defaultCSS()));
//    }
    
//    if(stringMatchQ(window.location.hostname, 'www*.wolfram.com') && stringMatchQ(window.location.pathname, '/download-center/')){
//        document.getElementById('_header').insertAdjacentHTML("afterend", message1(defaultCSS()));
//    }

//    if(stringMatchQ(window.location.hostname, 'www*.wolfram.com') && stringMatchQ(window.location.pathname, '/get-products-services/')){
//        document.getElementById('_header').insertAdjacentHTML("afterend", message1(defaultCSS()));
//    }
    
//    if(stringMatchQ(window.location.hostname, 'www*.wolfram.com') && stringMatchQ(window.location.pathname, '/desktop/system-requirements/')){
//        document.getElementById('_header').insertAdjacentHTML("afterend", message1(defaultCSS()));
//    }

//    if(stringMatchQ(window.location.hostname, 'www*.wolfram.com') && stringMatchQ(window.location.pathname, '/mathematica/')){
//        document.getElementById('_product-header').insertAdjacentHTML("afterend", message3(customCSS()));
//    }

//    if(stringMatchQ(window.location.hostname, 'www*.wolfram.com') && stringMatchQ(window.location.pathname, '/mathematica/pricing/*')){
//        document.getElementById('_header').insertAdjacentHTML("afterend", message1(defaultCSS()));
//    }
    
//    if(stringMatchQ(window.location.hostname, 'www*.wolfram.com') && stringMatchQ(window.location.pathname, '/mathematica/trial/')){
//        document.getElementById('_header').insertAdjacentHTML("afterend", message1(defaultCSS()));
//    }

//    if(stringMatchQ(window.location.hostname, 'www*.wolfram.com') && stringMatchQ(window.location.pathname, '/mathematica/system-requirements/')){
//        document.getElementById('_header').insertAdjacentHTML("afterend", message1(defaultCSS()));
//    }

//    if(stringMatchQ(window.location.hostname, 'www*.wolfram.com') && stringMatchQ(window.location.pathname, '/mathematica-personal-edition/')){
//        document.getElementById('_header').insertAdjacentHTML("afterend", message3(customCSS()));
//    }

//    if(stringMatchQ(window.location.hostname, 'www*.wolfram.com') && stringMatchQ(window.location.pathname, '/mathematica-student-edition/')){
//        document.getElementById('_header').insertAdjacentHTML("afterend", message3(customCSS()));
//    }

//    if(stringMatchQ(window.location.hostname, 'www*.wolfram.com') && stringMatchQ(window.location.pathname, '/promotions-discounts-offers/')){
//        document.getElementById('_header').insertAdjacentHTML("afterend", message1(defaultCSS()));
//    }

//    if(stringMatchQ(window.location.hostname, 'www*.wolfram.com') && stringMatchQ(window.location.pathname, '/system-modeler/')){
//        document.getElementById('_header').insertAdjacentHTML("beforebegin", message1(defaultCSS()));
//    }

//    if(stringMatchQ(window.location.hostname, 'www*.wolfram.com') && stringMatchQ(window.location.pathname, '/system-modeler/pricing/*')){
//        document.getElementById('_header').insertAdjacentHTML("afterend", message1(defaultCSS()));
//    }

//    if(stringMatchQ(window.location.hostname, 'www*.wolfram.com') && stringMatchQ(window.location.pathname, '/system-modeler/trial/')){
//        document.getElementById('_header').insertAdjacentHTML("beforebegin", message1(defaultCSS()));
//    }

//    if(stringMatchQ(window.location.hostname, 'www*.wolfram.com') && stringMatchQ(window.location.pathname, '/wolfram-one/')){
//        document.getElementById('_header').insertAdjacentHTML("afterend", message3(customCSS()));
//    }

//    if(stringMatchQ(window.location.hostname, 'www*.wolfram.com') && stringMatchQ(window.location.pathname, '/wolfram-one/pricing/*')){
//       document.getElementById('_header').insertAdjacentHTML("afterend", message1(defaultCSS()));
//    }

//    if(stringMatchQ(window.location.hostname, 'www*.wolfram.com') && stringMatchQ(window.location.pathname, '/wolfram-one/system-requirements/')){
//       document.getElementById('_header').insertAdjacentHTML("afterend", message1(defaultCSS()));
//    }

//    if(stringMatchQ(window.location.hostname, 'www*.wolfram.com') && stringMatchQ(window.location.pathname, '/wolfram-alpha-notebook-edition/')){
//        document.getElementById('_header').insertAdjacentHTML("afterend", message1(defaultCSS()));
//    }

//    if(stringMatchQ(window.location.hostname, 'www*.wolfram.com') && stringMatchQ(window.location.pathname, '/wolfram-alpha-notebook-edition/pricing/*')){
//        document.getElementById('_header').insertAdjacentHTML("afterend", message1(defaultCSS()));
//    }

//    if(stringMatchQ(window.location.hostname, 'www*.wolfram.com') && stringMatchQ(window.location.pathname, '/wolfram-alpha-notebook-edition/system-requirements/*')){
//        document.getElementById('_header').insertAdjacentHTML("afterend", message1(defaultCSS()));
//    }

//    if(stringMatchQ(window.location.hostname, 'www*.wolfram.com') && stringMatchQ(window.location.pathname, '/wolfram-u/registration/*')){
//        document.getElementById('_header').insertAdjacentHTML("afterend", message1(defaultCSS()));
//    }

//    if(stringMatchQ(window.location.hostname, 'www*.wolfram.com') && stringMatchQ(window.location.pathname, '/events/technology-conference/2026/registration/')){
//        document.getElementById('_header').insertAdjacentHTML("afterend", message1(defaultCSS()));
//    }

/***********************************************/
/* Level 3 Alerts                              */
/***********************************************/

//    if(stringMatchQ(window.location.hostname, 'reseller*.wolfram.com') && stringMatchQ(window.location.pathname, '/')){
//        document.getElementById('_header').insertAdjacentHTML("afterend", message1(defaultCSS()));
//    }

//	if(stringMatchQ(window.location.hostname, 'www*.wolfram.com') && stringMatchQ(window.location.pathname, '/cloud/')){
//		document.getElementById('_header').insertAdjacentHTML("afterend", message1(defaultCSS()));
//	}

//    if(stringMatchQ(window.location.hostname, 'www*.wolfram.com') && stringMatchQ(window.location.pathname, '/engine/')){
//        document.getElementById('_header').insertAdjacentHTML("afterend", message1(defaultCSS()));
//    }

//    if(stringMatchQ(window.location.hostname, 'www*.wolfram.com') && stringMatchQ(window.location.pathname, '/player/')){
//        document.getElementById('_header').insertAdjacentHTML("afterend", message1(defaultCSS()));
//    }

/***********************************************/
/* Other                                       */
/***********************************************/
    
//    if(stringMatchQ(window.location.hostname, 'www*.wolfram.com') && stringMatchQ(window.location.pathname, '/hackathons/')){
//        document.getElementById('header').insertAdjacentHTML("beforebegin", message3(customCSS()));
//    }   

/***********************************************/
/* End                                         */
/***********************************************/
 
});