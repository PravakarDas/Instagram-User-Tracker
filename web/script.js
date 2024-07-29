document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('fileInput');

    uploadForm.addEventListener('submit', function(event) {
        event.preventDefault();
        
        const file = fileInput.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const content = e.target.result;
                const instagramData = JSON.parse(content);
                updatePage(instagramData);
            };
            reader.readAsText(file);
        }
    });

    function updatePage(instagramData) {
        document.getElementById('totalFollowers').textContent = instagramData["Total Followers"];
        document.getElementById('totalFollowing').textContent = instagramData["Total Following"];

        populateList(instagramData["Not Following Back"], 'notFollowingBack', 'totalNotFollowingBack');
        populateList(instagramData["Unknown Followers"], 'unknownFollowers', 'totalUnknownFollowers');
        populateList(instagramData["Pending Follow Requests"], 'pendingFollowRequests', 'totalPendingFollowRequests');
        populateList(instagramData["Received Follow Requests"], 'receivedFollowRequests', 'totalReceivedFollowRequests');
    }

    function populateList(dataArray, listId, totalId) {
        const list = document.getElementById(listId);
        const total = document.getElementById(totalId);
        list.innerHTML = ''; // Clear previous items
        total.textContent = dataArray.length;

        dataArray.forEach((item, index) => {
            const listItem = document.createElement('li');
            listItem.classList.add('list-item');

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = `checkbox_${listId}_${index}`;
            listItem.appendChild(checkbox);

            const usernameLink = document.createElement('a');
            usernameLink.classList.add('username');
            usernameLink.href = item.href;
            usernameLink.target = '_blank'; // Open link in new tab
            usernameLink.textContent = `${index + 1}. ${item.value}`;
            listItem.appendChild(usernameLink);

            const hoverPopup = document.createElement('div');
            hoverPopup.classList.add('hover-popup');
            hoverPopup.innerHTML = `
                <p>Since ${item.timestamp}</p>
            `;
            listItem.appendChild(hoverPopup);

            usernameLink.addEventListener('mouseover', function() {
                hoverPopup.style.display = 'block';
            });

            usernameLink.addEventListener('mouseout', function() {
                hoverPopup.style.display = 'none';
            });

            list.appendChild(listItem);
        });
    }
});
