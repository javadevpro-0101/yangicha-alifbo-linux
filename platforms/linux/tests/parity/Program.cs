// Reference oracle: runs the real C# Core classes and mirrors KeyboardHook.TryConvertWord.
using System.Reflection;
using System.Text;
using YangiAlifbo.Core;
using YangiAlifbo.Win32;

static class Program
{
    static HashSet<string> Load(string resource)
    {
        var set = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        using var stream = Assembly.GetExecutingAssembly().GetManifestResourceStream(resource)!;
        using var reader = new StreamReader(stream, Encoding.UTF8);
        string? line;
        while ((line = reader.ReadLine()) != null)
        {
            var t = line.Trim();
            if (t.Length > 0 && !t.StartsWith('#')) set.Add(t);
        }
        return set;
    }

    // Same decision as KeyboardHook.TryConvertWord (src/Win32/KeyboardHook.cs).
    static string? TryConvertWord(string word, LanguageDetector det, bool aggressive, bool chatSlang)
    {
        if (string.IsNullOrWhiteSpace(word) || word.Length < 2) return null;
        if (det.IsForeignOrReject(word)) return null;

        string work = word;
        if (chatSlang) work = ChatNormalizer.Normalize(word);

        if (!UzbekPhonetics.HasConvertiblePatterns(work))
        {
            if (work != word && det.IsUzbek(work)) return work;
            return null;
        }
        if (aggressive) return UzbekPhonetics.Convert(work);
        if (det.IsUzbek(work)) return UzbekPhonetics.Convert(work);
        return null;
    }

    static void Main(string[] args)
    {
        var det = new LanguageDetector(Load("english_reject.txt"), Load("uzbek_words.txt"));
        if (args.Length > 2 && args[2] == "text")
        {
            // Text mode: whole lines through TextConverter.Convert (src/Core/TextConverter.cs).
            var lines = File.ReadAllLines(args[0], Encoding.UTF8);
            var tb = new StringBuilder();
            foreach (var line in lines)
            {
                foreach (var mode in new[] { TransliterationMode.Strict, TransliterationMode.Aggressive })
                {
                    string result = TextConverter.Convert(line, det, mode, true, out _);
                    tb.Append(line).Append('\t').Append(mode == TransliterationMode.Aggressive ? "aggressive" : "strict")
                      .Append('\t').Append(result).Append('\n');
                }
            }
            File.WriteAllText(args[1], tb.ToString(), new UTF8Encoding(false));
            Console.WriteLine($"wrote {lines.Length * 2} text rows");
            return;
        }
        var words = File.ReadAllLines(args[0], Encoding.UTF8);
        var sb = new StringBuilder();
        foreach (var w in words)
        {
            foreach (bool aggr in new[] { false, true })
            {
                string? r = TryConvertWord(w, det, aggr, true);
                sb.Append(w).Append('\t').Append(aggr ? "aggressive" : "strict").Append('\t').Append(r ?? "").Append('\n');
            }
        }
        File.WriteAllText(args[1], sb.ToString(), new UTF8Encoding(false));
        Console.WriteLine($"wrote {words.Length * 2} rows");
    }
}
