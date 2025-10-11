<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import browser from 'webextension-polyfill';

console.log('Hello from the popup!');

type SubscriptionsType = { [queue: string]: { action: string, state: boolean } };

const message = ref('');
const stomp = ref(false);
const subscriptions = ref<SubscriptionsType>({});

onMounted(async () => {
    const storage = await browser.storage.local.get(['stomp', 'subscriptions']);
    stomp.value = storage.stomp;
    if (storage.subscriptions) subscriptions.value = storage.subscriptions;
});

async function toggleNoStomp() {
    stomp.value = !stomp.value;
    await browser.storage.local.set({ stomp: stomp.value });
}

async function toggleSubscription(sub: keyof SubscriptionsType) {
    subscriptions.value[sub].state = !subscriptions.value[sub].state;
    await browser.storage.local.set({ subscriptions: subscriptions.value });
}

function startTask(action: string) {
    let data;
    try {
        data = JSON.parse(message.value);
    } catch (error) {
        data = {};
    }
    browser.runtime.sendMessage({
        action: action,
        data: data,
    });
}
</script>

<template>
    <div class="container">
        <div class="header">
            <img src="/icon-with-shadow.svg" alt="Extension Logo" />
            <h1>Universal Parser</h1>
            <div class="toggle-group">
                <label>STOMP Connection:</label>
                <div class="toggle-switch" @click="toggleNoStomp">
                    <div class="slider" :class="{ active: stomp }"></div>
                    <span class="state-text">{{ stomp ? 'ON' : 'OFF' }}</span>
                </div>
            </div>
        </div>

        <div v-if="stomp" class="subscriptions-container">
            <h3>Subscriptions:</h3>
            <div class="subscription-item" v-for="(value, key) in subscriptions" :key="key">
                <label>{{ key }}</label>
                <div class="toggle-switch small" @click="() => toggleSubscription(key)">
                    <div class="slider" :class="{ active: value.state }"></div>
                    <span class="state-text">{{ value.state ? 'ON' : 'OFF' }}</span>
                </div>
            </div>
        </div>

        <input
            type="text"
            class="json-input"
            placeholder="Put the task JSON data here..."
            v-model="message"
        >

        <div class="button-grid">
            <button
                v-for="(config, queue) in subscriptions"
                :key="config.action"
                @click="startTask(config.action)"
                class="action-button"
            >
                {{ `Start ${queue}` }}
            </button>
        </div>
    </div>
</template>

<style>
/* Добавим новые стили для списка подписок */
.subscriptions-container {
    background: #2a2a2a;
    padding: 12px;
    border-radius: 8px;
    margin-bottom: 10px;
}

.subscriptions-container h3 {
    margin-top: 0;
    margin-bottom: 10px;
    font-size: 0.9rem;
    color: #ccc;
}

.subscription-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 0;
    border-bottom: 1px solid #3a3a3a;
}

.subscription-item:last-child {
    border-bottom: none;
}

.subscription-item label {
    font-size: 0.85rem;
    text-transform: capitalize;
}

.toggle-switch.small {
    transform: scale(0.8);
    transform-origin: right;
}
html, body {
    width: 320px;
    min-height: 450px;
    padding: 0;
    margin: 0;
    font-family: 'Segoe UI', system-ui, sans-serif;
}

body {
    background: #1a1a1a;
    color: white;
}

.container {
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.header {
    text-align: center;
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.header img {
    width: 80px;
    height: 80px;
    margin: 0 auto;
}

h1 {
    font-size: 1.4rem;
    font-weight: 600;
    color: #fff;
    margin: 0;
}

.toggle-group {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    font-size: 0.9rem;
}

.toggle-switch {
    position: relative;
    display: flex;
    align-items: center;
    cursor: pointer;
    background: #333;
    border-radius: 15px;
    padding: 3px;
    transition: all 0.3s;
}

.slider {
    width: 24px;
    height: 24px;
    background: #666;
    border-radius: 50%;
    transition: all 0.3s;
    margin-right: 25px;
}

.slider.active {
    transform: translateX(26px);
    background: #4CAF50;
}

.state-text {
    position: absolute;
    right: 8px;
    font-size: 0.8rem;
    color: white;
}

.json-input {
    width: 100%;
    padding: 12px;
    border: 1px solid #444;
    border-radius: 8px;
    background: #2a2a2a;
    color: white;
    font-size: 0.9rem;
    outline: none;
    transition: border-color 0.3s;
}

.json-input:focus {
    border-color: #4CAF50;
}

.button-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
}

.action-button {
    padding: 12px 15px;
    border: none;
    border-radius: 8px;
    background: #3a3a3a;
    color: white;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
}

.action-button:hover {
    background: #4CAF50;
    transform: translateY(-1px);
}

.action-button:active {
    transform: translateY(0);
}
</style>