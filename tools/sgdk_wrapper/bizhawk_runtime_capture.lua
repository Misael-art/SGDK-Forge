local script_source = debug.getinfo(1, "S").source or ""
local script_path = script_source:match("^@(.*)$") or ""
local context_path = os.getenv("SGDK_RT_CONTEXT")
if (context_path == nil or context_path == "") and script_path ~= "" then
    context_path = script_path .. ".context"
end

local function load_context(path)
    if path == nil or path == "" then
        return {}
    end

    local handle = io.open(path, "r")
    if handle == nil then
        return {}
    end

    local context = {}
    for line in handle:lines() do
        local key, value = string.match(line, "^([A-Z0-9_]+)=(.*)$")
        if key ~= nil then
            context[key] = value
        end
    end

    handle:close()
    return context
end

local context = load_context(context_path)

local function read_setting(name, default)
    local value = rawget(_G, name)
    if value ~= nil then
        value = tostring(value)
    end
    if value == nil or value == "" then
        value = os.getenv(name)
    end
    if value == nil or value == "" then
        value = context[name]
    end
    if value == nil or value == "" then
        return default
    end
    return value
end

local output_path = read_setting("SGDK_RT_OUTPUT", nil)
local probe_address = tonumber(read_setting("SGDK_RT_PROBE_ADDR", nil))
local frame_window = tonumber(read_setting("SGDK_RT_FRAME_WINDOW", "1800")) or 1800
local target_scene = tonumber(read_setting("SGDK_RT_TARGET_SCENE", "0")) or 0
local perceptual_fluidez = tonumber(read_setting("SGDK_RT_PERCEPTUAL_FLUIDEZ", "0")) or 0
local perceptual_leitura = tonumber(read_setting("SGDK_RT_PERCEPTUAL_LEITURA", "0")) or 0
local perceptual_naturalidade = tonumber(read_setting("SGDK_RT_PERCEPTUAL_NATURALIDADE", "0")) or 0
local perceptual_impacto = tonumber(read_setting("SGDK_RT_PERCEPTUAL_IMPACTO", "0")) or 0
local heartbeat_path = read_setting("SGDK_RT_HEARTBEAT", nil)
local error_path = read_setting("SGDK_RT_ERROR", nil)
local max_wait_frames = math.max(frame_window + 600, 900)
local word_offset = 2
local sample_offset = 32

local function write_text(path, value)
    if path == nil or path == "" then
        return
    end

    local handle = io.open(path, "w")
    if handle == nil then
        return
    end

    handle:write(value)
    handle:close()
end

local function write_heartbeat(value)
    write_text(heartbeat_path, value)
end

local function read_word(index)
    return mainmemory.read_u16_be(probe_address + (index * word_offset))
end

local function json_escape(value)
    return tostring(value):gsub("\\", "\\\\"):gsub("\"", "\\\"")
end

local function percentile(sorted, ratio)
    local count = #sorted
    if count == 0 then
        return 0
    end

    local index = math.floor(((count - 1) * ratio) + 1)
    if index < 1 then
        index = 1
    end
    if index > count then
        index = count
    end

    return sorted[index]
end

local function collect_samples(count)
    local samples = {}
    for i = 0, count - 1 do
        samples[#samples + 1] = read_word(sample_offset + i)
    end
    return samples
end

local function average(samples)
    local total = 0
    for _, value in ipairs(samples) do
        total = total + value
    end
    if #samples == 0 then
        return 0
    end
    return total / #samples
end

local function write_report(status, timeout_frame)
    local samples_recorded = read_word(9)
    local samples = collect_samples(samples_recorded)
    table.sort(samples)

    local report = {
        "{",
        string.format('  "schema_version": %d,', read_word(2)),
        '  "source": "bizhawk_lua",',
        string.format('  "capture_status": "%s",', json_escape(status)),
        string.format('  "frame_window": %d,', frame_window),
        string.format('  "timeout_frame": %d,', timeout_frame),
        string.format('  "probe_magic_hi": %d,', read_word(0)),
        string.format('  "probe_magic_lo": %d,', read_word(1)),
        string.format('  "target_fps": %d,', read_word(4)),
        string.format('  "scene_id": %d,', read_word(5)),
        string.format('  "frames_seen": %d,', read_word(8)),
        string.format('  "samples_recorded": %d,', samples_recorded),
        string.format('  "over_budget_frames": %d,', read_word(10)),
        string.format('  "cpu_load_max": %d,', read_word(11)),
        string.format('  "cpu_load_jitter_max": %d,', read_word(13)),
        string.format('  "max_scanline_sprites": %d,', read_word(14)),
        string.format('  "fx_peak_concurrency": %d,', read_word(15)),
        string.format('  "sprite_engine_peak": %d,', read_word(16)),
        string.format('  "active_fx": %d,', read_word(17)),
        string.format('  "budget_threshold": %d,', read_word(23)),
        string.format('  "frame_cpu_ratio_avg": %.2f,', average(samples)),
        string.format('  "frame_cpu_ratio_p95": %d,', percentile(samples, 0.95)),
        '  "perceptual_check": {',
        string.format('    "fluidez": %d,', perceptual_fluidez),
        string.format('    "leitura": %d,', perceptual_leitura),
        string.format('    "naturalidade": %d,', perceptual_naturalidade),
        string.format('    "impacto": %d', perceptual_impacto),
        "  }",
        "}"
    }

    local handle = io.open(output_path, "w")
    if handle == nil then
        error("Nao foi possivel abrir o arquivo de saida: " .. tostring(output_path))
    end

    handle:write(table.concat(report, "\n"))
    handle:close()
end

if output_path == nil or probe_address == nil then
    error("SGDK_RT_OUTPUT e SGDK_RT_PROBE_ADDR sao obrigatorios.")
end

write_heartbeat("lua_loaded")

local ok, err = xpcall(function()
    local capture_status = "timeout"
    write_heartbeat("loop_start")
    client.unpause()

    while true do
        local frame = emu.framecount()
        if frame == 0 then
            write_heartbeat("frame_0_before_advance")
        end

        if frame >= 220 and frame < 228 then
            joypad.set({ ["P1 A"] = true, ["P1 Start"] = true, A = true, Start = true }, 1)
        else
            joypad.set({}, 1)
        end

        emu.frameadvance()
        client.unpause()

        local scene_id = read_word(5)
        local samples_recorded = read_word(9)
        if frame % 120 == 0 then
            write_heartbeat(string.format("frame=%d scene=%d samples=%d", frame, scene_id, samples_recorded))
        end

        if scene_id == target_scene and samples_recorded >= frame_window then
            capture_status = "ok"
            break
        end

        if frame >= max_wait_frames then
            break
        end
    end

    write_report(capture_status, max_wait_frames)
    write_heartbeat("report_written")
    client.pause()
    client.closerom()
    client.exitCode(0)
end, function(message)
    return debug.traceback(tostring(message), 2)
end)

if not ok then
    write_text(error_path, err)
    error(err)
end
