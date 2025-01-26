function getPageData() {
  // Locate the script element
  const scriptElement = document.children[0].children[1].children[8];

  // Extract the script's content
  const scriptContent = scriptElement.innerHTML;

  // Use a regex to match everything between "var _pageData = {" and the last "};"
  const match = scriptContent.match(/var\s+_pageData\s*=\s*\{([\s\S]*?)\};/);

  // If a match is found, parse it as JSON
  if (match) {
    try {
      // Reconstruct the JSON object by adding braces
      const pageData = JSON.parse(`{${match[1]}}`);

      // Check if mapdataJson exists and parse it as JSON
      if (pageData.mapdataJson) {
        pageData.mapdataJson = JSON.parse(pageData.mapdataJson);
      }

      return pageData;
    } catch (e) {
      console.error('Failed to parse _pageData or mapdataJson:', e);
      return null;
    }
  }

  // If no match is found, return null
  return null;
}

function downloadPageData() {
  const pageData = getPageData();
  if (!pageData) {
    console.error('Failed to retrieve page data.');
    return;
  }

  // Convert the pageData object to a JSON string
  const jsonData = JSON.stringify(pageData, null, 2);

  // Create a blob for the JSON data
  const blob = new Blob([jsonData], { type: "application/json" });

  // Create a download link
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "pageData.json"; // Name of the downloaded file
  document.body.appendChild(a);

  // Programmatically trigger the download
  a.click();

  // Clean up by removing the temporary link
  document.body.removeChild(a);
}

