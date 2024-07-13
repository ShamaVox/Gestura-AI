using System;
using System.Diagnostics;
using UnityEngine;

public static class PerformanceLogger
{
    private static Stopwatch stopwatch = new Stopwatch();

    public static void LogTiming(string operation, long elapsedMilliseconds)
    {
        UnityEngine.Debug.Log($"[PERF] {DateTime.Now:HH:mm:ss.fff} - {operation}: {elapsedMilliseconds}ms");
    }

    public static void LogMemoryUsage(string context)
    {
        long memoryUsage = GC.GetTotalMemory(false) / (1024 * 1024);
        UnityEngine.Debug.Log($"[MEM] {DateTime.Now:HH:mm:ss.fff} - {context}: {memoryUsage}MB");
    }

    public static void StartTimer()
    {
        stopwatch.Restart();
    }

    public static long StopTimer()
    {
        stopwatch.Stop();
        return stopwatch.ElapsedMilliseconds;
    }
}