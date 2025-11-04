SIGN_IN_URL = 'https://platform.agio.services/login'
SIGN_UP_URL = 'https://platform.agio.services/signup'
DOCS_URL = 'https://doki.agio.services'
SUPPORT_UEL = 'https://t.me/agio_support_bot'
WELCOME_TEXT = """
<html>
<body>

    <p>
        We're excited to have you on board!
    </p>
    <p>
        This installer will guide you through the installation process.<br/>
        To get started, simply click the <span style=\" font-weight:600;\">NEXT</span> button below.
    </p>
    <p>
        Let\u2019s get things set up!
    </p>
</body>
</html>
"""
DONE_TEXT = f'''
<html>
<body>
    <p><span style=" font-size:12pt; font-weight:600;">
        Thank you for installing agio.desk!</span>
    </p>
    <p>We appreciate you choosing our software. You're all set to begin using it.</p>
    <ul style="margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;">
    
        <li style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
            Want to access cloud features or manage your account? 
            <br>
            <a href="{SIGN_IN_URL}">
            Log in
            </a>
                or 
            <a href="{SIGN_UP_URL}">
                Create an account
            </a> 
            on our website.
         </li>
    
        <li style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
            For help getting started, visit our 
            <a href="{DOCS_URL}">
                <span style=" text-decoration: underline; color:#1d99f3;">
                    Getting Started Guide
                </span>
            </a>
        </li>
    
        <li style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
            For complete documentation, check out our <a href="{DOCS_URL}">
            <span style="text-decoration: underline; color:#1d99f3;">
                Full Docs
            </span>
            </a>
        </li>
    
        <li style="margin-top: 2px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
            Need support? Reach us anytime at 
            <a href="{SUPPORT_UEL}">
                <span style=" text-decoration: underline; color:#1d99f3;">
                    Support Chat
                </span>
            </a>
        </li>
    
</ul>
<p>We wish you all the best and hope you enjoy using <b>agio Platform!</b></p>
<p>\u2014 The agio band</p></body>
</html>
'''
