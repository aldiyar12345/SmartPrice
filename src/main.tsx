import React from "react";
import ReactDOM from "react-dom/client";
import SmartPriceLanding from "./SmartPriceLanding";
import "./main.css";

import { GoogleOAuthProvider } from "@react-oauth/google";
import { GoogleReCaptchaProvider } from "react-google-recaptcha-v3";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <GoogleOAuthProvider clientId="123456789-mock-client-id.apps.googleusercontent.com">
      <GoogleReCaptchaProvider reCaptchaKey="6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI">
        <SmartPriceLanding />
      </GoogleReCaptchaProvider>
    </GoogleOAuthProvider>
  </React.StrictMode>
);
