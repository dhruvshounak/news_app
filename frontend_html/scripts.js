const API_BASE_URL = "http://127.0.0.1:8000/api";

const categoryMapping = {
    tech: "tech",
    health: "health",
    business: "business",
    entertainment: "entertainment",
    science: "science",
    sports: "sports",
    politics: "politics",
    food: "food",
    travel: "travel",
    general: "general"
};

async function fetchNews(category, searchQuery = "") {
    try {
        const maxPage = 6666;
        const randomPage = Math.floor(Math.random() * maxPage) + 1;
        const timestamp = new Date().getTime();
        let url = `${API_BASE_URL}/news/news/?category=${category}&page=${randomPage}&_=${timestamp}`;
        if (searchQuery.trim() !== "") {
            url += `&search=${encodeURIComponent(searchQuery)}`;
        }        
        const response = await fetch(url, { cache: "no-store" });
        
        if (!response.ok) throw new Error("Failed to fetch news");

        const newsData = await response.json();
        console.log("Fetched News:", newsData);

        // Fetch summaries for each article
        const articlesWithSummaries = await Promise.all(
            newsData.data.map(async (article) => {
                try {
                    const summaryResponse = await fetch(`${API_BASE_URL}/news/summarized/${article.id}/`, { cache: "no-store" });
                    if (!summaryResponse.ok) throw new Error("Failed to fetch summary");
                    const summaryData = await summaryResponse.json();
                    return { ...article, summary: summaryData.summary };
                } catch (error) {
                    console.warn(`No summary for article ${article.id}:`, error);
                    return { ...article, summary: "Summarizing..." };
                }
            })
        );

        displayNews(articlesWithSummaries);
    } catch (error) {
        console.error("Error fetching news:", error);
        alert("Failed to load news. Please try again.");
    }
}

async function fetchTopNews() {
    try {
        const url = `${API_BASE_URL}/news/top/`;
        const response = await fetch(url, { cache: "no-store" });
        if (!response.ok) throw new Error("Failed to fetch news");
        const newsDataTop = await response.json();

        // Fetch summaries for each article
        const articlesWithSummaries = await Promise.all(
            newsDataTop.data.map(async (article) => {
                try {
                    const summaryResponse = await fetch(`${API_BASE_URL}/news/summarized/${article.id}/`, { cache: "no-store" });
                    if (!summaryResponse.ok) throw new Error("Failed to fetch summary");
                    const summaryData = await summaryResponse.json();
                    return { ...article, summary: summaryData.summary };
                } catch (error) {
                    console.warn(`No summary for article ${article.id}:`, error);
                    return { ...article, summary: "Summarizing..." };
                }
            })
        );

        displayNews(articlesWithSummaries);
    } catch (error) {
        console.error("Error fetching top news:", error);
        alert("Failed to load top news. Please try again.");
    }
}

function displayNews(newsList) {
    const newsContainer = document.getElementById("news-list");
    newsContainer.innerHTML = "";

    if (newsList.length === 0) {
        newsContainer.innerHTML = "<p>No news found for this category.</p>";
        return;
    }

    newsList.forEach(article => {
        const newsItem = document.createElement("div");
        newsItem.classList.add("news-card");

        // Add summary section above "Read More"
        const summaryClass = article.summary === "Summarizing..." ? "summary-loading" : "summary-section";
        newsItem.innerHTML = `
            <h3>${article.title}</h3>
            <img src="${article.image_url || 'https://via.placeholder.com/300'}" alt="News Image" class="news-image">
            <p>${article.description || "No description available."}</p>
            <div class="${summaryClass}">${article.summary}</div>
            <a href="${article.url}" target="_blank">Read More</a>
        `;

        newsContainer.appendChild(newsItem);
    });
}

document.querySelectorAll(".category-btn").forEach(button => {
    button.addEventListener("click", function () {
        const category = this.dataset.category;
        fetchNews(category);
    });
});

async function registerUser(event) {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    try {
        const response = await fetch(`${API_BASE_URL}/users/register/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, username, password }),
        });

        if (!response.ok) throw new Error("Registration failed");

        alert("Registration successful! You can now log in.");
        window.location.href = "login.html";
    } catch (error) {
        console.error("Error registering user:", error);
        alert("Failed to register. Please try again.");
    }
}

async function loginUser(event) {
    event.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    try {
        const response = await fetch(`${API_BASE_URL}/users/login/?nocache=${new Date().getTime()}`, {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "Cache-Control": "no-cache, no-store, must-revalidate",
            },
            body: JSON.stringify({ username, password }),
        });

        const data = await response.json();
        
        if (!response.ok || !data.access || !data.refresh) throw new Error("Login failed");

        localStorage.setItem("access_token", data.access);
        localStorage.setItem("refresh_token", data.refresh);
        alert("Login successful!");
        window.location.href = "index.html";
    } catch (error) {
        console.error("Error logging in:", error);
        alert("Invalid username or password. Please try again.");
    } 
}

function checkAuthStatus() {
    const token = localStorage.getItem("access_token");
    const loginLink = document.getElementById("login-link");
    const registerLink = document.getElementById("register-link");
    const profileLink = document.getElementById("profile-link");
    const logoutLink = document.getElementById("logout-link");

    if (token) {
        loginLink.style.display = "none";
        registerLink.style.display = "none";
        profileLink.style.display = "inline";
        logoutLink.style.display = "inline";

        profileLink.onclick = async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/users/profile/`, {
                    method: "GET",
                    headers: { "Authorization": `Bearer ${token}` }
                });

                if (!response.ok) throw new Error("Failed to fetch profile");

                const userData = await response.json();
                alert(`Username: ${userData.username}\nEmail: ${userData.email}`);
            } catch (error) {
                console.error("Error fetching profile:", error);
                alert("Failed to load profile.");
            }
        };
    } else {
        loginLink.style.display = "inline";
        registerLink.style.display = "inline";
        profileLink.style.display = "none";
        logoutLink.style.display = "none";
    }
}

function logoutUser() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    checkAuthStatus();
    alert("You have been logged out!");
    window.location.href = "index.html";
}

document.addEventListener("DOMContentLoaded", () => {
    if (window.location.pathname.includes("index.html") || window.location.pathname === "/") {
        fetchTopNews();
    }
    const registerForm = document.getElementById("register-form");
    const loginForm = document.getElementById("login-form");

    if (registerForm) registerForm.addEventListener("submit", registerUser);
    if (loginForm) loginForm.addEventListener("submit", loginUser);

    checkAuthStatus();

    const logoutButton = document.getElementById("logout-link");
    if (logoutButton) {
        logoutButton.addEventListener("click", (event) => {
            event.preventDefault();
            logoutUser();
        });
    }

    const searchButton = document.getElementById("search-button");
    if (searchButton) {
        searchButton.addEventListener("click", function () {
            const searchQuery = document.getElementById("search-input").value.trim();
            if (searchQuery !== "") {
                fetchNews("general", searchQuery);
            } else {
                console.warn("No search query entered.");
            }
        });
    }
});