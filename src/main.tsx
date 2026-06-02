import React from "react";
import ReactDOM from "react-dom/client";
import SmartPriceLanding from "./SmartPriceLanding";
import "./main.css";

import { GoogleOAuthProvider } from "@react-oauth/google";
import { GoogleReCaptchaProvider } from "react-google-recaptcha-v3";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <GoogleOAuthProvider clientId={import.meta.env.VITE_GOOGLE_CLIENT_ID || ""}>
      <GoogleReCaptchaProvider reCaptchaKey={import.meta.env.VITE_RECAPTCHA_SITE_KEY || ""}>
        <SmartPriceLanding />
      </GoogleReCaptchaProvider>
    </GoogleOAuthProvider>
  </React.StrictMode>
);
