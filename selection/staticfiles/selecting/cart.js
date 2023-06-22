function generateReports(){
    let checkBoxes = document.querySelectorAll('input[type="checkbox"]');
    var checkedId = [];

    checkBoxes.forEach(function(checkBox){
        if (checkBox.checked) {
            checkedId.push(checkBox.dataset.calc);   
            console.log(checkBox.dataset.calc); 
        }
    })
    console.log(checkedId);
}