function generateReports(){
    cal_ids = getCheckbox(selectAll=false)

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
      })
    .catch(function(error) {
        console.log('Error:', error.message);
    });

}

function deleteCartItemsd(selectAll){
    cal_ids = getCheckbox(selectAll=selectAll)
    fetch(`delete_cart_item/${cal_ids}`)
    .then(function(response) {
        if (response.ok) {
            return response.blob();
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
    if (checkBoxes.length == 0){
        return null;
    }

    var Ids =[];
    checkBoxes.forEach(function(checkBox){
        if (selectedAll){
            Ids.push(checkBox.dataset.calc);
        }
        else{
            if (checkBox.checked) {
                checkedIds.push(checkBox.dataset.calc);   
            }
        }
    })

    return Ids.join(',');
}