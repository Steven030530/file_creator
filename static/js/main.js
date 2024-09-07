
function regresar(){
    window.location.href = "/"
}

document.addEventListener('DOMContentLoaded',() => {
    const image = document.getElementById('idea');
    const textBox = document.getElementById('text-box');

    image.addEventListener('click',()=>{
        if (textBox.style.display == 'none' || textBox.style.display == ''){
            textBox.style.display = 'block'
        }else{
            textBox.style.display = 'none';
        }
    })
})

