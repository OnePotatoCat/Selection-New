function reveal(){
    var reveals = document.querySelectorAll(".reveal")

    revealDelay = 0
    for (var i=0; i < reveals.length; i++){
        var windowHeight = window.innerHeight;
        var elementTop = reveals[i].getBoundingClientRect().top;
        var elementVisible = 100;

        if (elementTop < windowHeight - elementVisible && !reveals[i].classList.contains("active")){
            revealDelay++;
            setTimeout(function (index){
                reveals[index].classList.add("active");
            }, 200*revealDelay, i);
        }
    }
}

window.addEventListener("scroll", reveal);

function downloadPdf(pdf){
    if (pdf == null){return}

    let headers = new Headers();
    const csrftoken = getCookie('csrftoken');
    headers.append('X-CSRFToken', csrftoken);

    fetch(`download_pdf/${pdf}`,{
        method: "POST",
        headers: headers,
    })
    .then(function(response) {
        if (response.ok) {
            return response.blob();
        }
        throw new Error('Network response was not OK');
    })
    .then(function(data) {
        const pdfURL = URL.createObjectURL(data);
        const link = document.createElement('a');
        link.href = pdfURL;
        link.download = pdf;
        link.style.display = 'none';
        document.body.appendChild(link);

        link.click();
        URL.revokeObjectURL(pdfURL);
        document.body.removeChild(link);
      })
    .catch(function(error) {
        console.log('Error:', error.message);
    });
}