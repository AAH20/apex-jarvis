# APEX_JARVIS Diagram Repository (Diagram-Design Standard)

This repository catalogs the formal architectural state machines and component graphs for **APEX_JARVIS**.

---

## 1. State Machine: Voice-to-Action Lifecycle with Compensating Rollback

```mermaid
stateDiagram-v2
    [*] --> AUDIO_STREAM_LISTEN: Mic Stream Active
    
    state AUDIO_STREAM_LISTEN {
        [*] --> EnergyThresholdPoll
        EnergyThresholdPoll --> VAD_Framing: Speech Energy > Threshold
        VAD_Framing --> ChunkedASR: VAD Silence Counter Triggered
    }

    ChunkedASR --> INTENT_ROUTING: Transcribed Intent Emitted

    state INTENT_ROUTING {
        [*] --> ClefSecurityCheck
        ClefSecurityCheck --> DeterministicCache: Intent Approved
        ClefSecurityCheck --> SecurityQuarantine: Dangerous Directive Detected
        DeterministicCache --> JevFastPath: Pattern Matched (O(1))
        DeterministicCache --> LayaNeuralQuery: Ambiguous Intent
    }

    SecurityQuarantine --> [*]: Voice Warning Dispatched

    JevFastPath --> ACTION_CONTRACT_EVAL: Action Resolved (0.001ms)
    LayaNeuralQuery --> ACTION_CONTRACT_EVAL: Action Resolved (4.200ms)

    state ACTION_CONTRACT_EVAL {
        [*] --> AssertPreCondition
        AssertPreCondition --> PushRollbackStack: Pre-State Valid
        AssertPreCondition --> AbortExecution: Pre-State Invalid
    }

    AbortExecution --> [*]: State Intact, Error Spoken
    PushRollbackStack --> DISPATCH_HARDWARE: Sub-Pixel Virtual HID

    state DISPATCH_HARDWARE {
        [*] --> InjectDirectEvent
        InjectDirectEvent --> AwaitSettlement
    }

    AwaitSettlement --> POST_CONDITION_ASSERT: Read Target State

    state POST_CONDITION_ASSERT {
        [*] --> VerifyPostCondition
        VerifyPostCondition --> ActionCommitted: Condition Met
        VerifyPostCondition --> TriggerRollback: Condition Failed
    }

    ActionCommitted --> PARALLEL_VOICE_FEEDBACK: Pop Rollback Stack
    TriggerRollback --> ROLLBACK_EXECUTION: Pop LIFO Stack

    state ROLLBACK_EXECUTION {
        [*] --> DispatchCompensatingInverse
        DispatchCompensatingInverse --> VerifyCleanState
    }

    VerifyCleanState --> PARALLEL_VOICE_FEEDBACK: Clean State Restored
    PARALLEL_VOICE_FEEDBACK --> [*]: Emit Visemes & Audio
```

---

## 2. Circular Audio Ring Buffer Architecture

```mermaid
flowchart TD
    subgraph AUDIO_PRODUCER["Hardware Audio Producer (Microphone / CoreAudio)"]
        MIC_THREAD["Audio Capture Callback (16kHz / 16-bit Mono)"]
        FRAME["10ms Frame: 320 Bytes (160 Samples)"]
        MIC_THREAD --> FRAME
    end

    subgraph AUDIO_RING["Lock-Free Audio Ring Buffer (Capacity: 512 Slots)"]
        SLOT_0["Slot 0: 320 Bytes"]
        SLOT_1["Slot 1: 320 Bytes"]
        SLOT_N["Slot N: 320 Bytes"]
        HEAD_PTR["Head Pointer (Consumer Read)"]
        TAIL_PTR["Tail Pointer (Producer Write)"]
        FRAME -->|Atomic Write| SLOT_0
    end

    subgraph AUDIO_CONSUMER["VAD & Speech Recognition Pipeline"]
        VAD_READER["VAD Energy Poller (<5ms Framing)"]
        ASR_TRANSCRIBER["Streaming ASR Tokenizer (<25ms)"]
        SLOT_0 -->|Zero-Copy Read| VAD_READER
        VAD_READER --> ASR_TRANSCRIBER
    end
```
