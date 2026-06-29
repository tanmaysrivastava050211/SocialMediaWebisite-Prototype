function getCookie(name) {
    const value = document.cookie.split('; ').find(row => row.startsWith(name + '='));
    return value ? decodeURIComponent(value.split('=')[1]) : '';
}

const csrfToken = getCookie('csrftoken');

const FALLBACK_AVATARS = ["https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=400&h=400&q=80","https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=400&h=400&q=80","https://images.unsplash.com/photo-1438761681033-6461ffad8d80?auto=format&fit=crop&w=400&h=400&q=80","https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=400&h=400&q=80","https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=400&h=400&q=80","https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=400&h=400&q=80"];
const FALLBACK_POST_IMAGES = ["https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=800&h=500&q=80","https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&h=500&q=80","https://images.unsplash.com/photo-1493246507139-91e8fad9978e?auto=format&fit=crop&w=800&h=500&q=80","https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=800&h=500&q=80","https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=800&h=500&q=80","https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?auto=format&fit=crop&w=800&h=500&q=80","https://images.unsplash.com/photo-1470770841072-f978cf4d019e?auto=format&fit=crop&w=800&h=500&q=80","https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=800&h=500&q=80","https://images.unsplash.com/photo-1511884642898-4c92249e20b6?auto=format&fit=crop&w=800&h=500&q=80","https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?auto=format&fit=crop&w=800&h=500&q=80","https://images.unsplash.com/photo-1472214103451-9374bd1c798e?auto=format&fit=crop&w=800&h=500&q=80","https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=800&h=500&q=80","https://images.unsplash.com/photo-1447752875215-b2761acb3c5d?auto=format&fit=crop&w=800&h=500&q=80","https://images.unsplash.com/photo-1433086966358-54859d0ed716?auto=format&fit=crop&w=800&h=500&q=80","https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?auto=format&fit=crop&w=800&h=500&q=80","https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?auto=format&fit=crop&w=800&h=500&q=80","https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&h=500&q=80","https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=800&h=500&q=80"];

function installImageFallbacks(rootElement = document) {
    rootElement.querySelectorAll('img').forEach((img, index) => {
        const applyFallback = () => {
            if (img.dataset.fallbackApplied === 'true') return;
            img.dataset.fallbackApplied = 'true';
            const isAvatar = img.classList.contains('avatar') || img.closest('.comment, .suggestion, .post-head, .profile-mini, .user-menu');
            const pool = isAvatar ? FALLBACK_AVATARS : FALLBACK_POST_IMAGES;
            img.src = pool[index % pool.length];
        };
        img.addEventListener('error', applyFallback);
        if (img.complete && img.naturalWidth === 0) applyFallback();
    });
}

installImageFallbacks();

async function postForm(url, data) {
    const response = await fetch(url, {
        method: 'POST',
        headers: {'X-CSRFToken': csrfToken, 'X-Requested-With': 'XMLHttpRequest'},
        body: data,
    });
    if (!response.ok) throw new Error('Request failed');
    return response.json();
}

document.addEventListener('click', async (event) => {
    const likeBtn = event.target.closest('.like-btn');
    if (likeBtn) {
        likeBtn.classList.add('pulse');
        try {
            const data = await postForm(likeBtn.dataset.url, new FormData());
            likeBtn.classList.toggle('liked', data.liked);
            likeBtn.querySelector('.like-count').textContent = data.like_count;
        } finally {
            setTimeout(() => likeBtn.classList.remove('pulse'), 320);
        }
    }

    const toggle = event.target.closest('.comment-toggle');
    if (toggle) {
        toggle.closest('.post-card').querySelector('.comments-panel').classList.toggle('open');
    }

    const followBtn = event.target.closest('.follow-btn');
    if (followBtn) {
        const data = await postForm(followBtn.dataset.url, new FormData());
        followBtn.textContent = data.following ? 'Unfollow' : 'Follow';
        followBtn.classList.toggle('following', data.following);
        const followers = document.querySelector('[data-followers-count]');
        const following = document.querySelector('[data-following-count]');
        if (followers) followers.textContent = data.followers_count;
        if (following) following.textContent = data.following_count;
    }
});

document.addEventListener('submit', async (event) => {
    const commentForm = event.target.closest('.comment-form');
    if (commentForm) {
        event.preventDefault();
        const input = commentForm.querySelector('input[name="content"]');
        if (!input.value.trim()) return;
        const data = await postForm(commentForm.dataset.url, new FormData(commentForm));
        const list = commentForm.closest('.comments-panel').querySelector('.comments-list');
        const div = document.createElement('div');
        div.className = 'comment fade-in';
        div.innerHTML = '<img src="' + data.comment.avatar + '" alt="' + data.comment.author + '"><p><strong>' + data.comment.author + '</strong> ' + data.comment.content + '<small>' + data.comment.created + '</small></p>';
        list.appendChild(div);
        commentForm.closest('.post-card').querySelector('.comment-count').textContent = data.comment_count;
        input.value = '';
    }

    const createForm = event.target.closest('.create-post');
    if (createForm) {
        event.preventDefault();
        const data = await postForm(createForm.action, new FormData(createForm));
        if (data.success) {
            document.querySelector('#feed').insertAdjacentHTML('afterbegin', data.post.html);
            installImageFallbacks(document.querySelector('#feed'));
            createForm.reset();
            createForm.querySelector('[data-counter]').textContent = '0';
            createForm.querySelector('.image-preview').classList.remove('visible');
            createForm.querySelector('.post-textarea').style.height = 'auto';
        }
    }
});

document.querySelectorAll('.post-textarea').forEach(textarea => {
    const counter = document.querySelector('[data-counter]');
    const resize = () => {
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
        if (counter) counter.textContent = textarea.value.length;
    };
    textarea.addEventListener('input', resize);
    resize();
});

document.querySelectorAll('.image-url-input').forEach(input => {
    input.addEventListener('input', () => {
        const preview = input.closest('form').querySelector('.image-preview');
        if (input.value.trim()) {
            preview.src = input.value.trim();
            preview.classList.add('visible');
        } else {
            preview.classList.remove('visible');
        }
    });
});

const loadMore = document.querySelector('#load-more');
if (loadMore) {
    loadMore.addEventListener('click', async () => {
        const feed = document.querySelector('#feed');
        const page = feed.dataset.nextPage;
        if (!page) return;
        loadMore.textContent = 'Loading...';
        const separator = window.location.href.includes('?') ? '&' : '?';
        const response = await fetch(window.location.href + separator + 'page=' + page, {headers: {'X-Requested-With': 'XMLHttpRequest'}});
        const data = await response.json();
        data.posts.forEach(post => feed.insertAdjacentHTML('beforeend', post.html));
        installImageFallbacks(feed);
        feed.dataset.nextPage = data.next_page || '';
        feed.dataset.hasNext = data.has_next ? 'true' : 'false';
        loadMore.textContent = 'Load More';
        if (!data.has_next) loadMore.remove();
    });
}
