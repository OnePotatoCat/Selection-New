function showHistory(pageNumber) {
    let headers = new Headers();
    const csrftoken = getCookie('csrftoken');
    headers.append('X-CSRFToken', csrftoken);
    
    fetch(`history?page=${pageNumber}`,{
        method: "POST",
        headers: headers,
    })
    .then(function(response) {
        if (response.ok) {
            return response.text();  
        }
        throw new Error('Network response was not OK');
    })
    .then(function(data) {
        document.getElementById('main').innerHTML = data;
        history.pushState({}, "", `history?page=${pageNumber}`);
        addPageLinks();
    })
    .catch(function(error) {
        console.log('Error:', error.message);
    });
}

function addPageLinks(){
    const pageLinks = document.querySelectorAll('.page-link');
    pageLinks.forEach(function(pageLink) {
        const pageNumber = pageLink.getAttribute('data-page-number');
        pageLink.addEventListener('click', function(event) {
            event.preventDefault();
            showHistory(pageNumber);
        });
    });
}
