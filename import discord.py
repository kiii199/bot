import discord
from discord.ext import commands
import yt_dlp
import asyncio

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'ytsearch5'
}

@bot.event
async def on_ready():
    print(f'✅ 봇이 로그인되었습니다: {bot.user.name}')

@bot.command(name='검색')
async def search_and_play(ctx, *, search: str):
    await ctx.send(f"🔍 '{search}'을(를) 검색 중입니다...")

    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(search, download=False)
            entries = info.get('entries', [])
    except Exception as e:
        return await ctx.send(f"❌ 검색 중 오류가 발생했습니다: {e}")

    if not entries:
        return await ctx.send("❌ 검색 결과가 없습니다. 다른 검색어를 입력해주세요.")

    results = entries[:5]
    message = "**🔎 검색 결과 (1~5번 중 선택해주세요):**\n"
    for i, entry in enumerate(results, 1):
        title = entry.get('title', '제목 없음')
        duration = entry.get('duration', 0)
        mins = duration // 60
        secs = duration % 60
        message += f"{i}. {title} ({mins}:{secs:02})\n"

    await ctx.send(message)

    def check(m):
        return (
            m.author == ctx.author and
            m.channel == ctx.channel and
            m.content.isdigit() and
            1 <= int(m.content) <= len(results)
        )

    try:
        reply = await bot.wait_for('message', timeout=20.0, check=check)
        choice = int(reply.content) - 1
        selected = results[choice]

        # ✅ 자동 음성 채널 입장
        if not ctx.voice_client:
            if ctx.author.voice and ctx.author.voice.channel:
                try:
                    await ctx.author.voice.channel.connect()
                    await ctx.send("🔊 음성 채널에 자동으로 들어갔어요.")
                except Exception as e:
                    return await ctx.send(f"❌ 음성 채널에 들어갈 수 없어요: {e}")
            else:
                return await ctx.send("❌ 먼저 음성 채널에 들어가주세요.")

        # ✅ 음악 재생
        with yt_dlp.YoutubeDL({'format': 'bestaudio'}) as ydl:
            info = ydl.extract_info(selected['webpage_url'], download=False)
            stream_url = info['url']
            title = info.get('title', '제목 없음')

        vc = ctx.voice_client
        vc.stop()
        vc.play(discord.FFmpegPCMAudio(stream_url, **FFMPEG_OPTIONS))
        await ctx.send(f"🎵 재생 중: **{title}**")

    except asyncio.TimeoutError:
        await ctx.send("⏰ 시간이 초과되었습니다. 다시 명령어를 입력해주세요.")
    except Exception as e:
        await ctx.send(f"❌ 음악 재생 중 오류가 발생했습니다: {e}")

# 여기에 디스코드 봇 토큰 입력
bot.run("MTM4OTczNTQ3NDY0MTI0NDE2MQ.GhKCap.8_qwaKJgArLnDo6ufbnvTWcUS2yangxtl2eN0s")
