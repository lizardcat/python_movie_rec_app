import streamlit as st
import pandas as pd

# Set page config as the first command
st.set_page_config(page_title="🎬 IMDb Movie Recommender", layout="wide")

# ----------------------------------------
# 1️⃣ Load IMDb Data (with Fixes)
# ----------------------------------------

@st.cache_data
def load_data():
    """
    Load IMDb dataset from a CSV file, clean it, and prepare it for filtering.
    """
    df = pd.read_csv("imdb_top_1000.csv", low_memory=False)

    # Strip column names of extra spaces
    df.columns = df.columns.str.strip()

    # Define valid columns based on dataset structure
    valid_columns = ["Poster_Link", "Series_Title", "Released_Year", "Certificate",
                     "Runtime", "Genre", "IMDB_Rating", "Overview", "Meta_score",
                     "Director", "Star1", "Star2", "Star3", "Star4", "No_of_Votes", "Gross"]

    # Filter only columns that exist in the dataset
    df = df[valid_columns].dropna()

    # Convert Year column to integer (handling errors)
    df["Released_Year"] = pd.to_numeric(df["Released_Year"], errors="coerce").fillna(0).astype(int)

    # Convert Genre column to list
    df["Genre"] = df["Genre"].str.split(", ")  # Convert genres from string to list

    # Clean the Gross column (remove currency symbols and convert to numeric)
    df["Gross"] = df["Gross"].replace({r'[^\d.]': ''}, regex=True)  # Remove symbols
    df["Gross"] = pd.to_numeric(df["Gross"], errors="coerce").fillna(0).astype(int)  # Convert to int

    return df

df = load_data()

# ----------------------------------------
# 2️⃣ Streamlit UI Setup
# ----------------------------------------

st.title("🎬 IMDb Movie Recommendation Tool")
st.sidebar.markdown("### 🎥 About")
st.sidebar.markdown(
    "This tool was created by **[Alex Raza](https://github.io/lizardcat)** and is based on the **IMDb Top 1000 Movies Dataset**. "
    "You can find the dataset here: [IMDb Top 1000 Dataset](https://www.kaggle.com/datasets/harshitshankhdhar/imdb-dataset-of-top-1000-movies-and-tv-shows)"
)

st.sidebar.header("🔍 Select Your Preferences")

# ----------------------------------------
# 3️⃣ User Input Filters
# ----------------------------------------

# Select Genre
all_genres = sorted(set(genre for sublist in df["Genre"].dropna() for genre in sublist))
selected_genre = st.sidebar.selectbox("🎭 Choose a Genre", all_genres)

# Select Decade (Dynamically Extracted)
all_decades = sorted({str(year)[:3] + "0s" for year in df["Released_Year"].dropna().astype(int)})
selected_decade = st.sidebar.selectbox("📅 Choose a Decade", ["Any"] + all_decades)

# Select Minimum IMDb Rating
min_rating = st.sidebar.slider("⭐ Minimum IMDb Rating", 0.0, 10.0, 7.0)

# Select Certificate (MPAA Rating)
certificates = sorted(df["Certificate"].dropna().unique().tolist())
selected_certificate = st.sidebar.selectbox("🎯 Choose a Certificate", ["Any"] + certificates)

# Filter by Director (Optional)
director_search = st.sidebar.text_input("🎮 Search by Director (Optional)")

# ----------------------------------------
# 4️⃣ Apply Filters & Recommend Movies
# ----------------------------------------

def filter_movies(genre, decade, rating, certificate, director):
    filtered_df = df[df["Genre"].apply(lambda x: genre in x)]  # Filter by genre
    filtered_df = filtered_df[filtered_df["IMDB_Rating"] >= rating]  # Filter by rating

    # Filter by decade
    if decade != "Any":
        decade_start = int(decade[:3] + "0")
        filtered_df = filtered_df[(filtered_df["Released_Year"] >= decade_start) & 
                                  (filtered_df["Released_Year"] < decade_start + 10)]

    # Filter by Certificate (MPAA)
    if certificate != "Any":
        filtered_df = filtered_df[filtered_df["Certificate"] == certificate]

    # Filter by Director (Case-insensitive)
    if director:
        filtered_df = filtered_df[filtered_df["Director"].str.contains(director, case=False, na=False)]

    return filtered_df  # Limit to top 6 recommendations

recommended_movies = filter_movies(selected_genre, selected_decade, min_rating, selected_certificate, director_search)

# ----------------------------------------
# 5️⃣ Display Recommendations with Posters
# ----------------------------------------

st.write(f"### 🍿 Recommended {selected_genre} Movies")

if not recommended_movies.empty:
    for index, row in recommended_movies.iterrows():
        col1, col2 = st.columns([1, 3])  # 1/3 ratio for poster and details

        with col1:
            st.image(row["Poster_Link"], width=150)  # Display movie poster

        with col2:
            st.subheader(f"{row['Series_Title']} ({int(row['Released_Year'])})")
            st.write(f"⭐ IMDb Rating: {row['IMDB_Rating']}")
            st.write(f"🎭 Genre: {', '.join(row['Genre'])}")
            st.write(f"🎯 Certificate: {row['Certificate']} | 🕒 Runtime: {row['Runtime']}")
            st.write(f"🎮 Directed by: {row['Director']}")
            st.write(f"👨 Starring: {row['Star1']}, {row['Star2']}, {row['Star3']}, {row['Star4']}")
            st.write(f"📚 Overview: {row['Overview']}")
            st.markdown("---")  # Separator for better UI
else:
    st.warning("❌ No movies found. Try adjusting your filters.")

# ----------------------------------------
# 6️⃣ Run Streamlit App
# ----------------------------------------

if __name__ == "__main__":
    st.sidebar.markdown("💡 *Tip: Search for your favorite director or choose a high rating for top picks!*")
