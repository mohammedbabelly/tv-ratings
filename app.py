import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="TV Show Ratings", page_icon="📺", layout="wide")

st.title("📺 TV Show Episode Ratings")
st.markdown("Check episode ratings before watching to avoid disappointment!")

# Search input
show_name = st.text_input("Enter TV Show Name:", placeholder="e.g., Breaking Bad, The Office, Game of Thrones")

if st.button("Search", type="primary") or show_name:
    if show_name:
        with st.spinner("Fetching ratings..."):
            try:
                # Search for the show
                search_url = f"https://api.tvmaze.com/search/shows?q={show_name}"
                response = requests.get(search_url)
                results = response.json()
                
                if not results:
                    st.error("Show not found. Try a different name.")
                else:
                    show = results[0]['show']
                    st.success(f"Found: **{show['name']}**")
                    
                    # Get all episodes
                    episodes_url = f"https://api.tvmaze.com/shows/{show['id']}/episodes"
                    episodes = requests.get(episodes_url).json()
                    
                    # Group by season
                    seasons_data = {}
                    for ep in episodes:
                        season = ep['season']
                        if season not in seasons_data:
                            seasons_data[season] = []
                        
                        rating = ep.get('rating', {}).get('average')
                        seasons_data[season].append({
                            'episode': ep['number'],
                            'name': ep['name'],
                            'rating': rating if rating else None
                        })
                    
                    # Display season summaries
                    st.markdown("---")
                    st.subheader("📊 Season Averages")
                    
                    cols = st.columns(min(len(seasons_data), 4))
                    for idx, (season, episodes) in enumerate(seasons_data.items()):
                        valid_ratings = [ep['rating'] for ep in episodes if ep['rating'] is not None]
                        if valid_ratings:
                            avg = sum(valid_ratings) / len(valid_ratings)
                            with cols[idx % 4]:
                                st.metric(
                                    label=f"Season {season}",
                                    value=f"{avg:.1f}/10",
                                    delta=f"{len(valid_ratings)} eps"
                                )
                    
                    # Plot ratings per season
                    st.markdown("---")
                    st.subheader("📈 Episode Ratings Over Time")
                    
                    fig = go.Figure()
                    
                    for season, episodes in seasons_data.items():
                        episode_numbers = [ep['episode'] for ep in episodes if ep['rating'] is not None]
                        ratings = [ep['rating'] for ep in episodes if ep['rating'] is not None]
                        names = [ep['name'] for ep in episodes if ep['rating'] is not None]
                        
                        if ratings:
                            fig.add_trace(go.Scatter(
                                x=episode_numbers,
                                y=ratings,
                                mode='lines+markers',
                                name=f'Season {season}',
                                text=names,
                                hovertemplate='<b>%{text}</b><br>Episode %{x}<br>Rating: %{y:.1f}/10<extra></extra>'
                            ))
                    
                    fig.update_layout(
                        xaxis_title="Episode Number",
                        yaxis_title="Rating",
                        yaxis_range=[5, 10],
                        hovermode='closest',
                        height=500
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Detailed episode list by season
                    st.markdown("---")
                    st.subheader("📋 Detailed Episode Ratings")
                    
                    selected_season = st.selectbox(
                        "Select Season:",
                        options=list(seasons_data.keys()),
                        format_func=lambda x: f"Season {x}"
                    )
                    
                    if selected_season:
                        season_eps = seasons_data[selected_season]
                        df = pd.DataFrame(season_eps)
                        df = df[df['rating'].notna()]  # Only show rated episodes
                        
                        if not df.empty:
                            df['rating'] = df['rating'].apply(lambda x: f"{x:.1f}")
                            df.columns = ['Episode', 'Title', 'Rating']
                            st.dataframe(
                                df,
                                hide_index=True,
                                use_container_width=True
                            )
                        else:
                            st.info(f"No ratings available for Season {selected_season}")
                    
            except Exception as e:
                st.error(f"Error fetching data: {str(e)}")
    else:
        st.info("👆 Enter a TV show name to get started!")

# Footer
st.markdown("---")
st.markdown("*Data provided by TVMaze API*")
