import { useEffect } from 'react';

const SDK_URL = 'https://console.catalyst.zoho.com/convokraft/assets/js/convokraft-chat-sdk.js';

export default function ConvoKraftBot() {
  useEffect(() => {
    const existing = document.querySelector(`script[src="${SDK_URL}"]`);
    if (!existing) {
      const script = document.createElement('script');
      script.src = SDK_URL;
      script.async = true;
      document.body.appendChild(script);
    }

    return () => {
      const script = document.querySelector(`script[src="${SDK_URL}"]`);
      if (script) script.remove();
    };
  }, []);

  return (
    <div className="fixed bottom-0 right-0 z-50" style={{ width: 330, height: 450 }}>
      <convokraft-chat-bot
        bot-name="helpinpatientbooking"
        project-id="52519000000090005"
        org-id="910312373"
      />
    </div>
  );
}
