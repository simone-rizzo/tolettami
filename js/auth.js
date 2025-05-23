document.addEventListener('DOMContentLoaded', () => {
    const headerAuthButtonsContainer = document.getElementById('header-auth-buttons');
    const sessionToken = localStorage.getItem('session_token');
    const user = JSON.parse(localStorage.getItem('user'));
    const currentPagePath = window.location.pathname.split('/').pop() || 'landing_page.html'; // Default to landing if path is empty

    const protectedPages = ['add_pet.html', 'my_pets.html', 'book_appointment.html', 'my_appointments.html', 'profile.html'];
    const publicPagesWithAuthHeader = ['landing_page.html', 'login.html', 'register.html'];


    if (protectedPages.includes(currentPagePath) && !sessionToken) {
        window.location.href = 'login.html';
        return; 
    }

    function checkLoginStatus() {
        if (!headerAuthButtonsContainer) {
            return;
        }

        if (sessionToken && user) {
            // User is logged in
            headerAuthButtonsContainer.innerHTML = `
                <div class="flex items-center gap-x-4 sm:gap-x-6 lg:gap-x-9">
                    <a href="landing_page.html" class="text-[#111714] text-sm font-medium leading-normal px-2 py-1 hover:text-[#38e07b]">Home</a>
                    <a href="my_pets.html" class="text-[#111714] text-sm font-medium leading-normal px-2 py-1 hover:text-[#38e07b]">My Pets</a>
                    <a href="my_appointments.html" class="text-[#111714] text-sm font-medium leading-normal px-2 py-1 hover:text-[#38e07b]">My Appointments</a>
                    <a href="profile.html" class="text-[#111714] text-sm font-medium leading-normal px-2 py-1 hover:text-[#38e07b]">Profile</a> 
                </div>
                <button id="logout-button" class="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-xl h-10 px-4 bg-[#f0f4f2] hover:bg-gray-200 text-[#111714] text-sm font-bold leading-normal tracking-[0.015em]">
                    <span class="truncate">Logout</span>
                </button>
            `;

            const logoutButton = document.getElementById('logout-button');
            if (logoutButton) {
                logoutButton.addEventListener('click', async () => {
                    try {
                        // No API call needed for logout if not implemented server-side for session invalidation
                        // const response = await fetch('/api/logout', { method: 'POST' });
                        // if (!response.ok) {
                        //     console.error('Logout failed on server:', await response.json());
                        // }
                    } catch (error) {
                        console.error('Error during logout API call (if any):', error);
                    } finally {
                        localStorage.removeItem('session_token');
                        localStorage.removeItem('user');
                        window.location.href = 'login.html';
                    }
                });
            }
        } else {
            // User is not logged in
            // Ensure correct buttons are shown on public pages that have the auth header
            if (publicPagesWithAuthHeader.includes(currentPagePath)) {
                 headerAuthButtonsContainer.innerHTML = `
                    <div class="flex items-center gap-9"> <!-- Placeholder for other public nav links if any -->
                         <a class="text-[#111714] text-sm font-medium leading-normal" href="landing_page.html#services">Services</a> <!-- Example link -->
                         <a class="text-[#111714] text-sm font-medium leading-normal" href="landing_page.html#pricing">Pricing</a> <!-- Example link -->
                    </div>
                    <div class="flex gap-2">
                        <a id="login-button-header" href="login.html" class="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-xl h-10 px-4 bg-[#38e07b] text-[#111714] text-sm font-bold leading-normal tracking-[0.015em] hover:bg-green-500">
                            <span class="truncate">Log In</span>
                        </a>
                        <a id="signup-button-header" href="register.html" class="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-xl h-10 px-4 bg-[#f0f4f2] text-[#111714] text-sm font-bold leading-normal tracking-[0.015em] hover:bg-gray-200">
                            <span class="truncate">Sign Up</span>
                        </a>
                    </div>
                `;
            } else if (!protectedPages.includes(currentPagePath)) {
                // For other public pages not explicitly listed, or if headerAuthButtonsContainer is present by mistake
                headerAuthButtonsContainer.innerHTML = ''; // Clear it or set a very minimal default
            }
        }
    }

    checkLoginStatus();

    // Specific for landing_page.html hero button
    const heroPrenotaButton = document.getElementById('hero-prenota-button');
    if (heroPrenotaButton) { // Check if the button exists on the current page
        if (sessionToken && user) {
            heroPrenotaButton.href = 'book_appointment.html';
        } else {
            heroPrenotaButton.href = 'login.html';
        }
    }
});
