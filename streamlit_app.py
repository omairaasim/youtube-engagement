import streamlit as st

import requests
import json

# YouTube API Key (replace with your own key)
API_KEY = "AIzaSyAJf1BQp-nlGar_c6R1ufCpfEyk2ezaCoE"
BASE_URL = "https://www.googleapis.com/youtube/v3"

# Function to get Channel ID from username
def get_channel_id(username):
    url = f"{BASE_URL}/channels?part=id&forHandle={username}&key={API_KEY}"
    response = requests.get(url).json()
    if "items" not in response or not response["items"]:
        raise ValueError("Invalid Username or API Key")
    return response["items"][0]["id"]

# Function to get Uploads Playlist ID
def get_uploads_playlist_id(channel_id):
    url = f"{BASE_URL}/channels?part=contentDetails&id={channel_id}&key={API_KEY}"
    response = requests.get(url).json()
    if "items" not in response or not response["items"]:
        raise ValueError("Invalid Channel ID or API Key")
    return response["items"][0]["contentDetails"]["relatedPlaylists"].get("uploads", "")

# Function to get latest video IDs sorted by published date
def get_latest_video_ids(playlist_id, max_results=10):
    if not playlist_id:
        raise ValueError("Invalid Playlist ID")
    url = f"{BASE_URL}/playlistItems?part=snippet&playlistId={playlist_id}&maxResults=20&key={API_KEY}&order=date"
    response = requests.get(url).json()
    
    videos = [
        {
            "video_id": item["snippet"]["resourceId"].get("videoId", ""),
            "published_at": item["snippet"].get("publishedAt", "")
        }
        for item in response.get("items", []) if "resourceId" in item["snippet"]
    ]
    
    # Sort videos by published date (descending order)
    videos = sorted(videos, key=lambda x: x["published_at"], reverse=True)
    return [v["video_id"] for v in videos[:max_results]]

# Function to get video stats (views, likes, comments)
def get_video_stats(video_ids):
    if not video_ids:
        raise ValueError("No video IDs found")
    video_ids_str = ",".join(video_ids)
    url = f"{BASE_URL}/videos?part=statistics&id={video_ids_str}&key={API_KEY}"
    response = requests.get(url).json()
    
    stats = []
    for item in response.get("items", []):
        video_id = item.get("id", "")
        views = int(item.get("statistics", {}).get("viewCount", 0))
        likes = int(item.get("statistics", {}).get("likeCount", 0))
        comments = int(item.get("statistics", {}).get("commentCount", 0))
        
        like_rate = (likes / views) * 100 if views > 0 else 0
        comment_rate = (comments / views) * 100 if views > 0 else 0
        engagement_rate = ((likes + comments) / views) * 100 if views > 0 else 0
        
        stats.append({
            "video_id": video_id,
            "views": views,
            "likes": likes,
            "comments": comments,
            "like_rate": round(like_rate, 2),
            "comment_rate": round(comment_rate, 2),
            "engagement_rate": round(engagement_rate, 2)
        })
    return stats

# Function to calculate average engagement rates
def calculate_average_rates(video_stats):
    if not video_stats:
        return {"like_rate": 0.0, "comment_rate": 0.0, "engagement_rate": 0.0}
    
    avg_like_rate = sum(v["like_rate"] for v in video_stats) / len(video_stats)
    avg_comment_rate = sum(v["comment_rate"] for v in video_stats) / len(video_stats)
    avg_engagement_rate = sum(v["engagement_rate"] for v in video_stats) / len(video_stats)
    
    return {
        "like_rate": round(avg_like_rate, 2),
        "comment_rate": round(avg_comment_rate, 2),
        "engagement_rate": round(avg_engagement_rate, 2)
    }

# Main function to get channel engagement rate
def get_channel_engagement_rate(username):
    try:
        channel_id = get_channel_id(username)
        playlist_id = get_uploads_playlist_id(channel_id)
        video_ids = get_latest_video_ids(playlist_id, max_results=50)
        video_stats = get_video_stats(video_ids)
        avg_rates = calculate_average_rates(video_stats)
        
        print(f"Channel Engagement Metrics for {username}:")
        print(f"- Average Like Rate: {avg_rates['like_rate']}%")
        print(f"- Average Comment Rate: {avg_rates['comment_rate']}%")
        print(f"- Average Engagement Rate: {avg_rates['engagement_rate']}%")
        return avg_rates
    except Exception as e:
        print(f"Error: {str(e)}")
        return None


st.title("🎈 Youtube Engagement")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)

username = st.text_input("Enter YouTube Channel Name:")
if st.button("Analyze"):
    result = get_channel_engagement_rate(username)
    st.write(result)


