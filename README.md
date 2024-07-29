**Instagram User Tracker**

**Project Overview**

The Instagram User Tracker project allows you to manage and track
interactions on your Instagram account. It helps you identify who
follows you, who has unfollowed you, and the status of your sent follow
requests that haven\'t been accepted. This tool is designed to make it
easier for users to manage their Instagram connections and understand
their social interactions better.

**Features**

-   **Track Followers and Following**: Identify who is following you and
    whom you are following.

-   **Pending Follow Requests**: See the accounts to which you have sent
    follow requests that haven\'t been accepted yet.

-   **Received Follow Requests**: View the accounts that have sent you
    follow requests.

-   **Identify Unfollowers**: Detect users who followed you and then
    unfollowed after you followed them back.

-   **Activity Timestamp**: Hover over an account ID to see when you
    followed the person or sent the follow request.

**Getting Started**

**Prerequisites**

-   Python 3.x installed on your system.

-   Instagram account to download your activity log.

**Instructions**

1.  **Download Your Instagram Activity Log**

    -   Go to your Instagram account.

    -   Navigate to: Your activity \> Download Your Information \>
        Download or Transfer Information.

    -   Select the Instagram profile, choose Some of your Information \>
        Connections \> Followers and following.

    -   Set Date Range to All time, Format to JSON, and Media quality to
        Low.

    -   Click CREATE FILES.

2.  **Download the Activity File**

    -   Instagram will send you a file once it\'s ready (this may take
        some time).

    -   Download the file when it becomes available.

3.  **Prepare the Files**

    -   Unzip the downloaded file.

    -   Go to the connections folder and then to
        followers_and_following.

    -   Copy follow_requests_you\'ve_received.json, followers_1.json,
        following.json, and pending_follow_requests.json to the assets
        folder of this project.

4.  **Run the Script**

    -   Execute the check.py file to process the data.

    -   A summary.json file will be generated in the same directory.

5.  **View the Results**

    -   Open index.html in the web folder.

    -   Upload the generated summary.json file.

    -   The web interface will display:

        -   Total Followers

        -   Total Following

        -   Accounts Not Following Back

        -   Unknown Followers

        -   Pending Follow Requests

        -   Received Follow Requests

**Usage**

This project helps you identify users who unfollow you after you follow
them, allowing you to manage your followers more effectively. It also
helps you recall which accounts you sent follow requests to but didn\'t
get accepted.

By logging into your Instagram account in the same browser, you can
navigate to corresponding accounts and manage your follow requests as
needed.
