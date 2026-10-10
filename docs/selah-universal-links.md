# Selah shared-reading domain association

This root-domain file is required by the Selah application PR352. The project repository cannot serve the root association path itself.

Publish `.well-known/apple-app-site-association` at `https://delight0517.github.io/.well-known/apple-app-site-association` without redirects. Only Selah project links with `homeAction=read` match. Team and iOS application identifier were read from the signed iOS94 build; Mac team/bundle identifier were read from installed Mac94.

This draft is not deployed. Current endpoint returned HTTP404 on 2026-10-10. After authorized merge: verify exact deployment commit, HTTP200 JSON body, Apple association CDN response, install updated entitled builds, and long-press/control-click a link from a different app/site. Safari same-domain navigation and the user's prior open-in-browser preference may keep navigation in the browser. An explicit Open in Selah link is retained as a user-controlled fallback.

Initial iOS95 build failed with No Accounts / missing Associated Domains. Existing ASC API authentication refreshed provisioning through workflow-control archive; archive succeeded and signed entitlements include applinks:delight0517.github.io. Source contract tests do not establish physical-device Universal Link routing. Never infer app absence from a timer or iframe probe.
