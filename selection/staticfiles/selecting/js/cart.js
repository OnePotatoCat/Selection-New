function showCart() {
    let headers = new Headers();
    const csrftoken = getCookie('csrftoken');
    headers.append('X-CSRFToken', csrftoken);
    
    fetch(`cart`,{
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
        history.pushState({}, "", `cart`);
    })
    .catch(function(error) {
        console.log('Error:', error.message);
    });
}


function generateReports(selectAll){
    cal_ids = getCheckbox(selectAll=selectAll)
    if (cal_ids == null){return}

    fetch(`generate_reports/${cal_ids}`)
    .then(function(response) {
        if (response.ok) {
            return response.blob();
        }
        throw new Error('Network response was not OK');
    })
    .then(function(data) {
        const zipURL = URL.createObjectURL(data);
        const link = document.createElement('a');
        link.href = zipURL;
        link.download = 'generate_pdfs.zip';
        link.style.display = 'none';
        document.body.appendChild(link);

        link.click();
        URL.revokeObjectURL(zipURL);
        document.body.removeChild(link);

        // TODO: Update History and Cart Page

        
      })
    .catch(function(error) {
        console.log('Error:', error.message);
    });

}

function deleteCartItems(selectAll){
    cal_ids = getCheckbox(selectAll=selectAll)
    if (cal_ids == null){return}

    fetch(`delete_cart_item/${cal_ids}`)
    .then(function(response) {
        if (response.ok) {
            return response.text();
        }
        throw new Error('Network response was not OK');
    })
    .then(function(data) {
        document.getElementById('main').innerHTML = data;
        history.pushState({}, "", `cart`);
    })
    .catch(function(error) {
        console.log('Error:', error.message);
    });

}


function getCheckbox(selectedAll){
    let checkBoxes = document.querySelectorAll('input[type="checkbox"]');
    if (checkBoxes.length == 0){return null;}

    var Ids =[];
    checkBoxes.forEach(function(checkBox){
        if (selectedAll){
            Ids.push(checkBox.dataset.calc);
        }
        else{
            if (checkBox.checked) {
                Ids.push(checkBox.dataset.calc);   
            }
        }
    })

    return Ids.length === 0 ? null : Ids.join(',');
}