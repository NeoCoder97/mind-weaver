import feedparser

# # 订阅源 URL（这里以 BBC 新闻 RSS 为例）
# rss_url = "http://feeds.bbci.co.uk/news/rss.xml"

# # 解析订阅源
# feed = feedparser.parse(rss_url)

atom_url = "https://wechat2rss.xlab.app/feed/5b925323244e9737c39285596c53e3a2f4a30774.xml"
feed = feedparser.parse(atom_url)

# 输出源信息
print("Feed 标题:", feed.feed.get("title"))
print("源链接:", feed.feed.get("link"))
print("描述:", feed.feed.get("description"))
print("-" * 40)

# 遍历每个条目
for entry in feed.entries:
    title = entry.get("title")
    link  = entry.get("link")
    published = entry.get("published", "无发布日期")

    print(f"标题: {title}")
    print(f"链接: {link}")
    print(f"发布日期: {published}")
    print("-" * 40)
