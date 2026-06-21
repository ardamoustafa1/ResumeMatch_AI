# Publishing the Chrome Extension

This guide covers the steps required to publish the NetworkForge extension to the Chrome Web Store.

## 1. Prepare the Extension
Run the build script from the root of the project to generate a clean zip file containing the extension.
```bash
make extension
```
This will produce a `resumematch-extension.zip` file in your project root, omitting unnecessary files like `.DS_Store`.

## 2. Google Chrome Web Store
1. Go to the [Chrome Developer Dashboard](https://chrome.google.com/webstore/devconsole/).
2. Click **New Item** and upload your `resumematch-extension.zip`.
3. Fill in the **Store Listing**:
   - **Title**: NetworkForge Job Matcher
   - **Description**: Add a compelling description highlighting the privacy-first matching.
   - **Icons & Screenshots**: Upload your 128x128 icon and at least one high-quality screenshot or video of the extension in action.
4. **Privacy Practices**:
   - Justify your use of `storage`, `activeTab`, and `scripting` permissions.
   - Assert that you are NOT collecting user data or transferring it improperly.
   - Provide a link to your hosted **Privacy Policy** (`https://<your-domain>/privacy`).
5. Submit for Review.

## 3. Firefox Add-ons (Optional)
If you wish to publish to Firefox AMO:
1. Go to the [Add-on Developer Hub](https://addons.mozilla.org/en-US/developers/).
2. Submit a New Add-on and upload the exact same zip file.
3. Firefox handles `manifest_version: 3` similarly, though review times may vary.
