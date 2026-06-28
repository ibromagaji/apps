import streamlit as st
import requests

# Set elegant, wide layout page configuration
st.set_page_config(
    page_title="Cinemix | Movie Discovery Hub",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SIDEBAR CONFIGURATION ---
st.sidebar.header("⚙️ Backend Configuration")
# Input for your localhost link
base_url = st.sidebar.text_input("FastAPI Base URL", value="http://127.0.0.1:8000").strip("/")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🍿 Navigation")
app_mode = st.sidebar.radio(
    "Choose a feature:",
    ["Search Movie", "Filter by Genre & Year", "Surprise Me!", "Trending Weekly"]
)

# Helper function to render a single TMDb movie object styled neatly
def display_tmdb_movie(movie):
    title = movie.get("title", movie.get("name", "Unknown Title"))
    release_date = movie.get("release_date", "N/A")
    rating = movie.get("vote_average", "N/A")
    overview = movie.get("overview", "No description available.")
    poster_path = movie.get("poster_path")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if poster_path:
            st.image(f"https://image.tmdb.org/t/p/w500{poster_path}", use_column_width=True)
        else:
            st.image("https://via.placeholder.com/500x750?text=No+Poster", use_column_width=True)
    with col2:
        st.subheader(title)
        st.markdown(f"**📅 Release Date:** {release_date}  |  **⭐ Rating:** {rating}/10")
        st.write(overview)
    st.markdown("---")


# --- MAIN APP INTERFACE ---
st.title("🎬 Cinemix Discovery Hub")
st.caption("A sleek Streamlit interface connected directly to your custom FastAPI movie agent.")
st.write("")

# 1. SEARCH ENDPOINT
if app_mode == "Search Movie":
    st.header("🔍 Search Specific Movie Details")
    movie_query = st.text_input("Enter Movie Title:", placeholder="e.g., Inception, Interstellar")
    
    if st.button("Search", type="primary"):
        if movie_query:
            with st.spinner("Searching OMDb API..."):
                try:
                    response = requests.get(f"{base_url}/search", params={"movie": movie_query})
                    if response.status_code == 200:
                        data = response.json()
                        
                        if "Error" in data:
                            st.warning(f"⚠️ {data['Error']}")
                        else:
                            col1, col2 = st.columns([1, 2])
                            with col1:
                                # Fallback image block since OMDb returns a Poster field if available
                                # Note: Your backend explicit return omits 'Poster', but if you add it back, you can render it here!
                                st.image("https://via.placeholder.com/400x550?text=Movie+Details", use_column_width=True)
                            with col2:
                                st.header(data.get("Title"))
                                st.subheader(f"📅 {data.get('Year')} | ⏳ {data.get('Runtime')} | ⭐ {data.get('imdbRating')}/10")
                                st.markdown(f"**🎬 Director:** {data.get('Director')}")
                                st.markdown(f"**🎭 Actors:** {data.get('Actors')}")
                                st.markdown(f"**🏷️ Genre:** {data.get('Genre')} | **📺 Type:** {data.get('Type')}")
                                st.info(f"**Plot Overview:**\n\n{data.get('Plot')}")
                    else:
                        st.error(f"Backend returned an error status: {response.status_code}")
                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to FastAPI server. Please check your Localhost URL or ensure your backend is running.")
        else:
            st.warning("Please type a movie name first.")

# 2. FILTER ENDPOINT
elif app_mode == "Filter by Genre & Year":
    st.header("🎯 High-Rated Genre Discovery")
    st.write("Finds up to 3 top-tier movies ($\ge 8.0$ rating) based on your criteria.")
    
    # Available genres matched to your backend keys
    available_genres = ['action', 'comedy', 'drama', 'sci-fi', 'horror', 'crime', 'romance', 'thriller', 'animation', 'fantasy', 'adventure']
    
    col1, col2 = st.columns(2)
    with col1:
        selected_genre = st.selectbox("Select Genre", options=available_genres)
    with col2:
        selected_year = st.number_input("Select Release Year", min_value=1900, max_value=2030, value=2024, step=1)
        
    if st.button("Discover Movies", type="primary"):
        with st.spinner("Filtering highly rated blockbusters..."):
            try:
                response = requests.get(f"{base_url}/filter", params={"genre": selected_genre, "year": selected_year})
                if response.status_code == 200:
                    movies = response.json()
                    if not movies:
                        st.info("No highly rated movies found matching that specific criteria.")
                    elif isinstance(movies, str) and "Error" in movies:
                        st.error(movies)
                    else:
                        for movie in movies:
                            display_tmdb_movie(movie)
                else:
                    st.error(f"Error connecting to server: Status code {response.status_code}")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to FastAPI server.")

# 3. SURPRISE ME ENDPOINT
elif app_mode == "Surprise Me!":
    st.header("🎲 Random Popular Pick")
    st.write("Can't decide what to watch? Let our random engine pick a popular flick for you.")
    
    if st.button("🎲 Roll the Dice", type="primary"):
        with st.spinner("Spinning the wheel..."):
            try:
                response = requests.get(f"{base_url}/suprise")
                if response.status_code == 200:
                    movie = response.json()
                    display_tmdb_movie(movie)
                else:
                    st.error("Error drawing a random selection from the backend.")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to FastAPI server.")

# 4. TRENDING ENDPOINT
elif app_mode == "Trending Weekly":
    st.header("🔥 Top 10 Trending Movies This Week")
    st.write("Stay up-to-date with what everyone else is watching.")
    
    if st.button("Fetch Trending List", type="primary"):
        with st.spinner("Fetching global charts..."):
            try:
                response = requests.get(f"{base_url}/trending")
                if response.status_code == 200:
                    trending_movies = response.json()
                    for idx, movie in enumerate(trending_movies, start=1):
                        st.markdown(f"### **#{idx}**")
                        display_tmdb_movie(movie)
                else:
                    st.error("Error retrieving trending data.")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to FastAPI server.")