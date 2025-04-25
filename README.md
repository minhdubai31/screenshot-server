## **How to run:**

1.  Install Docker and Docker Compose.
2.  Run the following command:
    `docker-compose up` 

## **Example Request:**

The server will run on port **5000**. Here's an example request:

`http://localhost:5000/screenshot?url=https://animevietsub.lol/` 

## **Notes:**

-   The `url` parameter must start with `http` or `https`.
-   A request may take **more than 8 seconds** because it simulates opening a browser, accessing the website, and capturing a screenshot.  This delay is necessary to bypass Cloudflare's bot protection.
