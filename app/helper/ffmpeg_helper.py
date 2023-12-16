import json
import subprocess

import log
from app.utils import SystemUtils


class FfmpegHelper:

    @staticmethod
    def has_vaapi():
        """
        判断系统是否支持 VA-API（核显加速）
        """
        try:
            # 运行 ls -l /dev/dri 命令并捕获输出
            result = subprocess.run(['ls', '-l', '/dev/dri'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output = result.stdout + result.stderr

            # 检查输出中是否包含相关设备信息，这里使用 renderD 作为判断标志
            if 'renderD' in output:
                return True
            else:
                return False

        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def get_thumb_image_from_video(video_path, image_path, frames="00:03:01"):
        """
        使用ffmpeg从视频文件中截取缩略图
        """
        if not video_path or not image_path:
            return False

        if FfmpegHelper.has_vaapi():
            # 使用核显加速
            cmd = 'ffmpeg -init_hw_device vaapi=/dev/dri/renderD128 -hwaccel vaapi -hwaccel_output_format vaapi ' \
                  '-i "{video_path}" -ss {frames} -vframes 1 -vf "format=nv12|vaapi,hwupload" ' \
                  '-f image2 "{image_path}"'.format(video_path=video_path, frames=frames, image_path=image_path)
        else:
            # 没有核显加速
            cmd = 'ffmpeg -i "{video_path}" -ss {frames} -vframes 1 -f image2 "{image_path}"'.format(
                video_path=video_path, frames=frames, image_path=image_path)
        log.info("【FfmpegHelper】cmd：%s " % cmd)
        log.info("【FfmpegHelper】是否调用vaapi：%s " % FfmpegHelper.has_vaapi())
        result = SystemUtils.execute(cmd)
        if result:
            return True
        return False

    @staticmethod
    def extract_wav_from_video(video_path, audio_path, audio_index=None):
        """
        使用ffmpeg从视频文件中提取16000hz, 16-bit的wav格式音频
        """
        if not video_path or not audio_path:
            return False

        # 提取指定音频流
        if audio_index:
            command = ['ffmpeg', "-hide_banner", "-loglevel", "warning", '-y', '-i', video_path,
                       '-map', f'0:a:{audio_index}',
                       '-acodec', 'pcm_s16le', '-ac', '1', '-ar', '16000', audio_path]
        else:
            command = ['ffmpeg', "-hide_banner", "-loglevel", "warning", '-y', '-i', video_path,
                       '-acodec', 'pcm_s16le', '-ac', '1', '-ar', '16000', audio_path]

        ret = subprocess.run(command).returncode
        if ret == 0:
            return True
        return False

    @staticmethod
    def get_video_metadata(video_path):
        """
        获取视频元数据
        """
        if not video_path:
            return False

        try:
            command = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', video_path]
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                return json.loads(result.stdout.decode("utf-8"))
        except Exception as e:
            print(e)
        return None

    @staticmethod
    def extract_subtitle_from_video(video_path, subtitle_path, subtitle_index=None):
        """
        从视频中提取字幕
        """
        if not video_path or not subtitle_path:
            return False

        if subtitle_index:
            command = ['ffmpeg', "-hide_banner", "-loglevel", "warning", '-y', '-i', video_path,
                       '-map', f'0:s:{subtitle_index}',
                       subtitle_path]
        else:
            command = ['ffmpeg', "-hide_banner", "-loglevel", "warning", '-y', '-i', video_path, subtitle_path]
        ret = subprocess.run(command).returncode
        if ret == 0:
            return True
        return False
