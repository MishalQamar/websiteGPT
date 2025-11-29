import streamlit as st
from utils import start_crawling,set_openai_api_key,generate_pinecone_database

st.title("Website Scraper")
st.caption("Crawl your website and build a searchable knowledge base")

# Sidebar
with st.sidebar:
    st.markdown("### Settings")
    st.markdown("---")
    
    user_api_key = st.text_input(
        label="OpenAI API Key",
        placeholder="sk-xxxxxx",
        type="password",
        value=st.session_state.get("openai_api_key", "") or "",
        help="Required for generating embeddings"
    )
    
    if user_api_key:
        st.session_state.openai_api_key = user_api_key
        set_openai_api_key(user_api_key)
        st.success("✓ Configured")
    else:
        st.caption("Enter your API key to continue")

# Main content
if user_api_key:
    st.session_state.openai_api_key = user_api_key
    set_openai_api_key(user_api_key)
    
    # Input form in a clean layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        website_url = st.text_input(
            label="Website URL",
            placeholder="https://example.com",
            help="Starting URL for crawling"
        )
    
    with col2:
        depth = st.slider(
            "Crawl Depth",
            min_value=0,
            max_value=5,
            value=1,
            help="Number of levels to crawl"
        )
    
    prefix_url = st.text_input(
        label="URL Prefix Filter",
        placeholder="https://example.com",
        help="Only URLs starting with this prefix will be included"
    )
    
    st.markdown("---")
    
    if 'scrapped_urls' not in st.session_state:
        st.session_state.scrapped_urls = []
    
    if website_url and prefix_url:
        # Button with proper sizing
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            process_button = st.button("Start Crawling", type="primary", use_container_width=False)
        
        if process_button:
            # Crawling section
            with st.spinner("Crawling URLs..."):
                try:
                    scrapped_urls = start_crawling(website_url, prefix_url, depth)
                    st.session_state.scrapped_urls = scrapped_urls
                    
                    if scrapped_urls:
                        st.markdown("---")
                        
                        # Results display
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**Found {len(scrapped_urls)} URLs**")
                        with col2:
                            st.caption(f"Depth: {depth}")
                        
                        with st.expander("View all URLs", expanded=False):
                            for i, url in enumerate(sorted(scrapped_urls), start=1):
                                st.code(url, language=None)
                        
                        # Generate database
                        with st.spinner("Building knowledge base..."):
                           generate_pinecone_database(scrapped_urls)
                        
                        st.success("Knowledge base is ready!")
                    else:
                        st.warning("No URLs found matching the prefix filter.")
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    else:
        st.info("Please fill in both Website URL and Prefix URL to begin")
else:
    st.info("👈 Enter your OpenAI API key in the sidebar to get started")
