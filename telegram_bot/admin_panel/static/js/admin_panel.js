function showSection(sectionId) {
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => {
        section.classList.remove('active');
    });
    const section = document.getElementById(sectionId);
    if (section) {
        section.classList.add('active');
    }
}

function getSectionFromUrl() {
    const path = window.location.pathname;
    const section = path.split('/').filter(Boolean).pop();
    return section || 'active_groups';
}

function loadSection(section) {
    fetch(`/${section}/`)
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const sectionElement = doc.querySelector('.section');
            document.querySelector('.content').innerHTML = sectionElement.outerHTML;
            showSection(section);
        })
        .catch(error => console.error('Error loading section:', error));
}

function previewImage(event) {
    const input = event.target;
    const preview = document.getElementById("preview");

    if (input.files && input.files[0]) {
        const reader = new FileReader();

        reader.onload = function(e) {
            preview.src = e.target.result;  // 🔹 Встановлюємо URL вибраного фото
            preview.style.display = "block";  // 🔹 Робимо зображення видимим
        };

        reader.readAsDataURL(input.files[0]);  // 🔹 Читаємо файл у base64
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const section = getSectionFromUrl();
    loadSection(section);
});

document.querySelectorAll('.sidebar a').forEach(link => {
    link.addEventListener('click', (event) => {
        event.preventDefault();
        const section = new URL(link.href).pathname.split('/').filter(Boolean).pop();
        loadSection(section);
        history.pushState(null, '', link.href);
    });
});

window.addEventListener('popstate', () => {
    const section = getSectionFromUrl();
    loadSection(section);
});

let protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
let socket = new WebSocket(protocol + window.location.host + "/ws/groups/");

socket.onmessage = function(event) {
    let data = JSON.parse(event.data);
    console.log("Отримано дані:", data);

    if (data.action === "update") {
        let group = data.group;
        let groupElements = document.querySelectorAll("#groups li");
        let groupElement = Array.from(groupElements).find(el => el.innerText.includes(group.group_name));

        if (groupElement) {
            groupElement.innerHTML = `Group: ${group.group_name} - Active: ${group.is_active}`;
        }
    }
};

socket.onopen = function() {
    console.log("WebSocket підключено!");
};

socket.onclose = function() {
    console.log("WebSocket відключено!");
};