// Copy paste into the Contacts page (https://www.zazzle.com/my/account/contacts)
const csrfToken = ZENV.csrf;

// The URL for the deletion endpoint
const deleteUrl = 'https://www.zazzle.com/svc/z3/connections/delete';

// Headers to mimic the curl request
const headers = {
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0',
  'Accept': 'application/json',
  'Accept-Language': 'en-US,en;q=0.5',
  'Content-Type': 'application/json',
  'Origin': 'https://www.zazzle.com',
  'Referer': 'https://www.zazzle.com/my/account/contacts',
  'X-Csrf-Token': csrfToken
};

// Check if ZData and its connections property exist
if (ZData && ZData.entities && ZData.entities.connections) {
  // Get all keys from the connections object
  const userIds = Object.keys(ZData.entities.connections);

  // Loop through each user ID and make a delete request
  userIds.forEach(userId => {
    // Construct the request body
    const requestBody = {
      connectionsUserId: userId,
      client: 'js'
    };

    console.log(`Attempting to delete connection for user ID: ${userId}`);

    // Make the fetch call
    fetch(deleteUrl, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(requestBody)
    })
    .then(response => {
      if (!response.ok) {
        // Handle non-successful responses
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json(); // Assuming the server responds with JSON
    })
    .then(data => {
      console.log(`Successfully deleted connection for user ID: ${userId}`, data);
    })
    .catch(error => {
      console.error(`Failed to delete connection for user ID: ${userId}`, error);
    });
  });
} else {
  console.error("ZData.entities.connections object not found.");
}
